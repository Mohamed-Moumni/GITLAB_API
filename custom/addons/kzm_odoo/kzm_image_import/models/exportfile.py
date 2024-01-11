from odoo import models


class ExportFile(models.AbstractModel):
    _name = 'report.kzm_image_import.export_file'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        for rec in datas:
            report_name = 'Canevas %s' % (
                rec.name)
            worksheet = workbook.add_worksheet(report_name)

            format1 = workbook.add_format(
                {'font_size': 8, 'bg_color': 'd6dce5', 'align': 'center', 'valign': 'vcenter',
                 'font_color': 'black', 'bold': True, 'border': 1})

            worksheet.set_row(0, 15)

            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 15)

            worksheet.write('A1:A1', 'Correspondance (Id, Id externe, reference ...)', format1)
            worksheet.write('B1:B1', rec.field_id.name, format1)
