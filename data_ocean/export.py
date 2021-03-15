import boto3
from botocore.config import Config
from datetime import datetime
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Alignment, fonts, PatternFill
from openpyxl.utils.cell import get_column_letter

from django.apps import apps
from django.conf import settings

from business_register import filters


class ExportToXlsx:

    @staticmethod
    def export(params, export_dict, model_name):
        queryset = apps.get_model('business_register', model_name).objects.all()
        export_filterset_class = getattr(filters, model_name + 'ExportFilterSet')
        queryset = export_filterset_class(params,  queryset).qs

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = model_name
        worksheet.sheet_properties.tabColor = '0033CCCC'
        worksheet.row_dimensions[1].height = 20
        worksheet.freeze_panes = 'A2'
        for col_num, (column_title, column_properties) in enumerate(export_dict.items(), 1):
            row_num = 1
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = column_title
            worksheet.column_dimensions[get_column_letter(col_num)].width = column_properties[1]
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.font = fonts.Font(b=True)
            cell.fill = PatternFill(bgColor='0033CCCC', fill_type="solid")
            for record in queryset:
                cell_value = getattr(record, column_properties[0])
                row_num += 1
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.alignment = Alignment(vertical='top', wrap_text=True)
                cell.value = cell_value
        export_file_name = model_name + '_{0}.xlsx'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        data = BytesIO()
        workbook.save(data)
        data = data.getvalue()
        config = Config(
            region_name=settings.PROJECT_SERVER_AWS_REGION_NAME
        )
        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=config
        )
        s3.Bucket('pep-xlsx').put_object(Key=export_file_name, Body=data, ACL='public-read')
        return settings.PEP_EXPORT_FOLDER_URL + export_file_name
