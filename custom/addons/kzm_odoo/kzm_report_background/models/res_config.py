# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    background_application = fields.Boolean(string="appliquer l'arrière plan")
    pagination_section = fields.Boolean(string="Afficher pagination section", default=True)
    pagination_height = fields.Integer(string="Pagination height", default=15)


class ReportLayout(models.Model):
    _inherit = "report.layout"

    background_view_id = fields.Many2one('ir.ui.view')


class BaseDocuments(models.TransientModel):
    _inherit = "base.document.layout"

    background_application = fields.Boolean(string="appliquer l'arrière plan",
                                            related='company_id.background_application', readonly=False)
    pagination_section = fields.Boolean(related='company_id.pagination_section', readonly=False)
    pagination_height = fields.Integer(related='company_id.pagination_height', readonly=False)

    @api.onchange('background_application')
    def check_background_application(self):
        if self.background_application:
            paperformat = self.env.ref('kzm_report_background.paperformat_euro_for_background', False)
        else:
            paperformat = self.env.ref('base.paperformat_euro', False)
        self.write({'paperformat_id': paperformat.id})

    # @api.onchange('report_layout_id', 'background_application')
    # def _onchange_report_layout_id(self):
    #     for wizard in self:
    #         if wizard.background_application:
    #             wizard.external_report_layout_id = wizard.report_layout_id.background_view_id
    #         else:
    #             super(BaseDocuments, self)._onchange_report_layout_id()
