from odoo.http import route, request
from odoo.addons.portal.controllers.mail import PortalChatter


class CustomPortalChatter(PortalChatter):

    def edit_line_id(self, record, line_id):
        pass

    def portal_run_chatgpt(self, record, message):
        chatgpt_obj = request.env['chatgpt.request']
        response, line_id = chatgpt_obj.run_chatgpt(message)
        if line_id:
            self.edit_line_id(record, line_id)
        if response:
            chatgpt_obj.post_chatgpt_message(record, response)

    @route(['/mail/chatter_post'], type='json', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, attachment_ids=None, attachment_tokens=None, **kw):
        result = super().portal_chatter_post(res_model, res_id, message, attachment_ids=attachment_ids,
                                             attachment_tokens=attachment_tokens, **kw)
        record = request.env[res_model].sudo().browse(res_id)
        self.portal_run_chatgpt(record, message)
        return result
