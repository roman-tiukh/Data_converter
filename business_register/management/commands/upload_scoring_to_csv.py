import io
import json
import os
from datetime import datetime
import csv
from business_register.management.commands._base_export_command import BaseExportCommand
from business_register.models.declaration_models import PepScoring, Declaration
from business_register.pep_scoring.rules_registry import ScoringRuleEnum
from data_ocean import s3bucket


class Command(BaseExportCommand):
    help = '---'

    def add_arguments(self, parser):
        # parser.add_argument('rule_id', type=str, choices=[rule.value for rule in ScoringRuleEnum], nargs=1)
        parser.add_argument('-y', '--year', dest='year', nargs='?', type=int)
        parser.add_argument('-s', '--s3', dest='s3', action='store_true')
        parser.add_argument('-z', '--with_zero', dest='with_zero', action='store_true')
        parser.add_argument(
            '-r', '--rules', type=str, action='append',
            choices=[rule.value for rule in ScoringRuleEnum]
        )
        parser.add_argument(
            '-e', '--exclude', type=str, action='append',
            choices=[rule.value for rule in ScoringRuleEnum]
        )

    def handle(self, *args, **options):
        rules = options['rules']
        exclude = options['exclude']
        year = options['year']
        upload_scoring_with_zero = options['with_zero']
        export_to_s3 = options['s3']

        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow([
            'Посилання на декларацію',
            'Рік декларації',
            'Дата подання декларації',
            'PEP ID (pep.org.ua)',
            'PEP ID (dataocean)',
            'Посилання на PEP',
            'Повне ім\'я PEP',
            'ID правила',
            'Вирахувана вага',
            'Додаткові дані',
        ])
        qs = PepScoring.objects.filter(declaration__type=Declaration.ANNUAL)
        if rules:
            qs = qs.filter(rule_id__in=rules)
        elif exclude:
            qs = qs.exclude(rule_id__in=exclude)
        qs = qs.select_related(
            'declaration', 'pep',
        ).order_by(
            'rule_id',
            '-declaration__year',
            '-pep_id',
            '-declaration__submission_date',
        ).distinct('rule_id', 'declaration__year', 'pep_id')
        if year:
            qs = qs.filter(declaration__year=year)
        if not upload_scoring_with_zero:
            qs = qs.filter(score__gt=0)

        i = 0
        count = qs.count()
        if count == 0:
            self.stdout.write('No data for saving')
            return
        for ps in qs:
            i += 1
            self.stdout.write(f'\rProgress: {i} of {count}', ending='')
            self.stdout.flush()
            writer.writerow([
                ps.declaration.nacp_url,
                ps.declaration.year,
                ps.declaration.submission_date.strftime('%d.%m.%Y'),
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
        file_name = 'pep_scoring_'
        if year:
            file_name += f'{year}_'
        if rules:
            file_name += f'{"_".join(rules)}_'
        file_name += f'{now_str}.csv'

        if export_to_s3:
            url = s3bucket.save_file(f'scoring/{file_name}', data)
        else:
            url = self.save_to_file(file_name, data)

        with open(os.path.join(self.get_export_dir(), 'scoring_urls.txt'), 'a') as file:
            file.write(f'{url}\n')

        self.print('Done!', success=True)
        self.print(url, success=True)
