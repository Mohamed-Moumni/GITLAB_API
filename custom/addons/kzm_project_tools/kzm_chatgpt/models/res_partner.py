from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    chatgpt_request_ids = fields.One2many('chatgpt.request', 'partner_id')
