from odoo.http import route, request
from odoo.addons.portal.controllers.mail import PortalChatter


class CustomPortalChatter(PortalChatter):

    def get_default_values(self):
        user = request.env.user
        domain = [
            '|', '|', ('customer_id', '=', user.partner_id.id),
            ('secondary_customer_ids', 'in', user.partner_id.id),
            ('contact_ids', 'in', user.partner_id.id),
        ]
        contract_id = request.env['contract.cadre'].sudo().search(domain, limit=1)

        domain = [
            ('partner_id', '=', user.partner_id.id),
        ]
        conversations = request.env['chatgpt.conversation'].sudo().search(domain)
        values = {
            'contract_id': contract_id,
            'conversations': conversations if contract_id else [],
        }
        return values

    @route(['/open-chat-online'], type='http', auth="public", website=True)
    def portal_open_chat_online(self, **kw):
        values = self.get_default_values()
        return request.render("kzm_chatgpt.openticket_form", values)

    @route(['/conversations'], type='http', auth="public", website=True)
    def portal_conversations(self, **kw):
        values = self.get_default_values()
        return request.render("kzm_chatgpt.portal_conversation_list", values)

    @route(['/open-chat-online/submit'], type='http', auth="public", website=True, methods=["POST"])
    def open_chat_form_submit(self, sujet, description, **kwargs):
        user = request.env.user
        values = self.get_default_values()
        contract_id = values.get('contract_id', False)

        if not contract_id:
            values = {
                'error': True,
            }
            return request.render("kzm_chatgpt.openticket_form", values)

        conversation_id = request.env['chatgpt.conversation'].sudo().create({
            'name': sujet,
            'partner_id': user.partner_id.id,
            'description': description,
            'contract_id': contract_id.id,
        })
        self.portal_run_chatgpt(conversation_id, description)

        return self.conversation_followup(conversation_id.id)

    @route([
        '/my/conversation/<int:conversation_id>',
        '/my/conversation/<int:conversation_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def conversation_followup(self, conversation_id=None, access_token=None, **kw):
        values = self.get_default_values()
        conversation = request.env['chatgpt.conversation'].browse(conversation_id)
        values.update({
            'conversation': conversation,
        })
        return request.render("kzm_chatgpt.portal_conversation", values)

    def edit_line_id(self, record, line_id):
        line_id.write({
            'conversation_id': record.id,
        })
        values = self.get_default_values()
        contract_id = values.get('contract_id', False)
        if contract_id:
            line_id.write({
                'contract_id': contract_id.id,
            })

    def portal_run_chatgpt(self, record, message):
        values = self.get_default_values()
        contract_id = values.get('contract_id', False)
        if contract_id and contract_id.tag_ids:
            tag_ids = contract_id.tag_ids.mapped('name')
            tags = ', '.join(tag_ids)
            message = tags + ' : ' + message

        min_tokens = request.env.company.min_tokens
        if contract_id and contract_id.remained_tokens >= min_tokens and record._name == 'chatgpt.conversation':
            super().portal_run_chatgpt(record, message)
