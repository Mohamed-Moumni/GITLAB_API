# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import itemgetter

from markupsafe import Markup

from odoo import http
from odoo.http import request

from odoo.addons.helpdesk.controllers.portal import CustomerPortal
from odoo.addons.kzm_chatgpt.controllers.PortalChatter import CustomPortalChatter


class CustomCustomerPortal(CustomerPortal):

    @http.route(['/ticket-chat-online/<int:conversation_id>'], type='http', auth="public", website=True)
    def portal_open_ticket_chat_online(self, conversation_id=None, **kw):
        values = CustomPortalChatter().get_default_values()
        conversation = request.env['chatgpt.conversation'].browse(conversation_id)
        contract_id = values.get('contract_id', False)
        if contract_id and conversation:
            ticket_id = conversation.ticket_id.sudo()
            if not ticket_id:
                ticket_id = request.env['helpdesk.ticket'].sudo().create({
                    'name': conversation.name,
                    'partner_id': conversation.partner_id.id,
                    'description': conversation.description,
                    'contract_id': contract_id.id
                })
                conversation.ticket_id = ticket_id
                for chat in conversation.message_ids:
                    chat.sudo().copy({'model': 'helpdesk.ticket', 'res_id': ticket_id.id})
            return self.tickets_followup(ticket_id=ticket_id.id)
