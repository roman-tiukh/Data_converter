import io
import json
import os
from datetime import datetime
import csv
from business_register.management.commands._base_export_command import BaseExportCommand
from business_register.models.declaration_models import PepScoring
from business_register.pep_scoring.rules_registry import ScoringRuleEnum
from data_ocean import s3bucket


class Command(BaseExportCommand):
    help = '---'

    def add_arguments(self, parser):
        parser.add_argument('rule_id', type=str, choices=[rule.value for rule in ScoringRuleEnum], nargs=1)
        parser.add_argument('-y', '--year', dest='year', nargs='?', type=int)
        parser.add_argument('-s', '--s3', dest='s3', action='store_true')
        parser.add_argument('-a', '--all', dest='all', action='store_true')

    def handle(self, *args, **options):
        rule_id = options['rule_id'][0]
        year = options['year']
        upload_all = options['all']
        export_to_s3 = options['s3']

        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow([
            'Посилання на декларацію',
            'Рік декларації',
            'PEP ID (pep.org.ua)',
            'PEP ID (dataocean)',
            'Посилання на PEP',
            'Повне ім\'я PEP',
            'ID правила',
            'Вирахувана вага',
            'Додаткові дані',
        ])
        qs = PepScoring.objects.filter(rule_id=rule_id)
        if year:
            qs = qs.filter(declaration__year=year)
        if not upload_all:
            qs = qs.filter(score__gt=0)

        i = 0
        count = qs.count()
        if count == 0:
            self.stdout.write('No data for saving')
            return
        for ps in qs.order_by('pep_id'):
            i += 1
            self.stdout.write(f'\r Process {i} of {count}', ending='')
            self.stdout.flush()
            writer.writerow([
                ps.declaration.nacp_url,
                ps.declaration.year,
                ps.pep.source_id,
                ps.pep.id,
                ps.pep.pep_org_ua_link,
                ps.pep.fullname,
                ps.rule_id,
                ps.score,
                json.dumps(ps.data, ensure_ascii=False),
            ])

        self.stdout.write()
        self.stdout.write('Start saving file')

        data = stream.getvalue()
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        if year:
            file_name = f'pep_scoring_{year}_{rule_id}_{now_str}.csv'
        else:
            file_name = f'pep_scoring_{rule_id}_{now_str}.csv'

        if export_to_s3:
            url = s3bucket.save_file(f'scoring/{file_name}', data)
        else:
            url = self.save_to_file(file_name, data)

        with open(os.path.join(self.get_export_dir(), 'scoring_urls.txt'), 'a') as file:
            file.write(f'{url}\n')

        self.print('Done!', success=True)
        self.print(url, success=True)
