from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    bulk_sms_key = fields.Char(string="API BULK SMS Key")
    active_sms = fields.Boolean()