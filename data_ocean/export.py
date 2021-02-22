from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment, fonts, PatternFill
from openpyxl.utils.cell import get_column_letter

from django.conf import settings


class Export_to_xlsx():

    def export(self, queryset, export_dict, worksheet_title):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = worksheet_title
        worksheet.sheet_properties.tabColor = '0033CCCC'
        worksheet.row_dimensions[1].height = 20
        worksheet.freeze_panes = 'A2'
        for col_num, (column_title, query_field) in enumerate(export_dict.items(), 1):
            row_num = 1
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = column_title
            worksheet.column_dimensions[get_column_letter(col_num)].width = 30
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.font = fonts.Font(b=True)
            cell.fill = PatternFill(bgColor='0033CCCC', fill_type="solid")
            for record in queryset:
                sell_value = getattr(record, query_field)
                row_num += 1
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.alignment = Alignment(vertical='top', wrap_text=True)
                try:
                    cell.value = sell_value
                except:
                    cell.value = repr(sell_value)
        export_file_path = settings.EXPORT_FOLDER + 'fop_{0}.xlsx'.format(
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        if workbook.save(export_file_path):
            return export_file_path
