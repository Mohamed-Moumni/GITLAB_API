from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    referenced = fields.Boolean(default=False, string="Référencé")

    def validate_reference(self):
        for rec in self:
            rec.referenced = True

    def cancel_reference(self):
        for rec in self:
            rec.referenced = False
