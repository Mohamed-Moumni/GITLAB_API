from odoo import api, fields, models


class ContratCadre(models.Model):
    _inherit = 'contract.cadre'

    token_balance = fields.Integer(string="Token Balance")
    consumed_tokens = fields.Integer(string="Consumed Tokens", compute="_compute_consumed_tokens", store=True)
    remained_tokens = fields.Integer(string="Remained Tokens", compute="_compute_remained_tokens", store=True)
    chatgpt_request_line_ids = fields.One2many('chatgpt.request.line', 'contract_id')

    tag_ids = fields.Many2many('chatgpt.tag', string="Key Words")

    @api.depends('token_balance', 'consumed_tokens')
    def _compute_remained_tokens(self):
        for record in self:
            record.remained_tokens = record.token_balance - record.consumed_tokens

    @api.depends('chatgpt_request_line_ids', 'chatgpt_request_line_ids.total_tokens')
    def _compute_consumed_tokens(self):
        for record in self:
            record.consumed_tokens = sum(record.chatgpt_request_line_ids.mapped('total_tokens'))
