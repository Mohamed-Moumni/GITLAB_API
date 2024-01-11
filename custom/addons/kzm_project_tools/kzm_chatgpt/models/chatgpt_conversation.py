# -*- coding: utf-8 -*-
from odoo import fields, models


class ChatgptConversation(models.Model):
    _name = 'chatgpt.conversation'
    _description = 'chatgpt.conversation'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'utm.mixin', 'mail.activity.mixin']

    name = fields.Char(string='Nom')
    description = fields.Html()
    partner_id = fields.Many2one('res.partner', string='Client')
    contract_id = fields.Many2one('contract.cadre', string='Contract Cadre')

    line_ids = fields.One2many('chatgpt.request.line', 'conversation_id')

    ticket_id = fields.Many2one('helpdesk.ticket')

