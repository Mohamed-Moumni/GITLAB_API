from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    active_sms = fields.Boolean(related='company_id.active_sms', store=1, readonly=False)
    bulk_sms_key = fields.Char(related='company_id.bulk_sms_key', store=1, readonly=False)
