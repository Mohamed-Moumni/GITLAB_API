from odoo import api, fields, models


class ChatgptRequestLine(models.Model):
    _inherit = 'chatgpt.request.line'

    conversation_id = fields.Many2one('chatgpt.conversation', string="Conversation")
    contract_id = fields.Many2one('contract.cadre', string='Contract Cadre')
