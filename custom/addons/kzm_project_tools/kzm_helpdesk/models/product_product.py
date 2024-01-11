
from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.template'

    operation_id = fields.Many2one('helpdesk.ticket.type',string="Operation")


