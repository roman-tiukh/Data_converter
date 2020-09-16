import abc
from django.db import connection
from rest_framework import views
from rest_framework.response import Response
from data_ocean.views import CachedViewMixin


class BaseQuery(abc.ABC):
    @abc.abstractmethod
    def get_data(self, options):
        raise NotImplementedError


class RegistrationQuery(BaseQuery):
    tables = {
        'fop_registration': 'business_register_fop',
        'company_registration': 'business_register_company',
    }

    format_for_group_by = {
        'day': 'YYYY-MM-DD',
        'month': 'YYYY-MM',
        'year': 'YYYY',
    }

    group_by_sql = {
        'day': "date_part('year', registration_date), date_part('doy', registration_date)",
        'month': "date_part('year', registration_date), date_part('month', registration_date)",
        'year': "date_part('year', registration_date)",
    }

    def __init__(self, metric):
        self.table_name = self.tables[metric]

    def get_data(self, options):
        date_from = options['date_from']
        date_to = options['date_to']
        group_by = options['group_by']

        with connection.cursor() as cursor:
            cursor.execute(f"""
            select to_char(date_trunc('{group_by}', offs), '{self.format_for_group_by[group_by]}') AS date
            FROM generate_series('{date_from}'::timestamp, '{date_to}', '1 {group_by}') AS offs;
            """)
            data = {row[0]: 0 for row in cursor.fetchall()}

            cursor.execute(f'''
            SELECT to_char(max(registration_date), '{self.format_for_group_by[group_by]}') as date,
                    count(*) as count
            FROM {self.table_name}
            WHERE
                registration_date >= '{date_from}' AND
                registration_date <= '{date_to}'
            GROUP BY {self.group_by_sql[group_by]}
            ORDER BY max(registration_date)
            ''')

            for row in cursor.fetchall():
                data[row[0]] = row[1]
            return data.items()


class KvedQuery(BaseQuery):
    def __init__(self, metric_name):
        if metric_name == 'company_kved':
            self.rel_table = 'business_register_companytokved'
            self.table = 'business_register_company'
            self.count_col = 'company_id'
        elif metric_name == 'fop_kved':
            self.rel_table = 'business_register_foptokved'
            self.table = 'business_register_fop'
            self.count_col = 'fop_id'
        else:
            raise ValueError(f'Not supported metric name - {metric_name}')

    def get_data(self, options):
        kveds = options['kveds']
        kveds_sql: list = [f"'{x}'" for x in kveds]

        kveds = {kved: 0 for kved in kveds}

        with connection.cursor() as cursor:
            sql = f'''
            SELECT kved.code, count({self.count_col}) as count
            FROM {self.rel_table}
            JOIN {self.table} company on {self.rel_table}.{self.count_col} = company.id
            JOIN business_register_kved kved on {self.rel_table}.kved_id = kved.id
            WHERE kved.code IN ({','.join(kveds_sql)})
            GROUP BY kved.code
            ORDER BY kved.code
            '''
            cursor.execute(sql)
            for row in cursor.fetchall():
                kveds[row[0]] = row[1]
            return kveds.items()


class ReportBuilder:
    metric_map = {
        'fop_registration': RegistrationQuery('fop_registration'),
        'company_registration': RegistrationQuery('company_registration'),
        'fop_kved': KvedQuery('fop_kved'),
        'company_kved': KvedQuery('company_kved'),
    }

    def __init__(self, json_data: dict):
        self.type = json_data['type']
        assert self.type in ('date', 'kved')
        self.metrics = json_data['metrics']
        self.options = json_data['options']

    @property
    def data(self):
        data = {}
        for metric in self.metrics:
            data[metric] = self.metric_map[metric].get_data(self.options)
        return data


class ReportBuilderView(CachedViewMixin, views.APIView):
    def post(self, request):
        builder = ReportBuilder(request.data)
        return Response(builder.data, status=200)
