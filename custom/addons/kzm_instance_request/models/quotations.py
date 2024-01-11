from odoo import models, fields

class quotations(models.Model):
    _inherit = "sale.order"

    version_odoo_id = fields.Many2one('odoo.version', string="Odoo Versions")
