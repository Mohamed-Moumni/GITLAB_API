from odoo import models, api, _
from odoo.tools import html2plaintext, plaintext2html
import logging

_logger = logging.getLogger(__name__)


class MailThreadCustom(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_sms(self, body, subtype_id=False, partner_ids=False, number_field=False,
                     sms_numbers=None, sms_pid_to_number=None, **kwargs):
        if self.env.user.company_id.active_sms:

            return self.message_post(
                body="SMS Sent Successfully :" + plaintext2html(html2plaintext(body)),
                partner_ids=partner_ids or [],
                message_type='sms', subtype_id=subtype_id,
                sms_numbers=sms_numbers, sms_pid_to_number=sms_pid_to_number,
                **kwargs
            )
        else:
            return super(MailThreadCustom, self)._message_sms(
                body=body, subtype_id=subtype_id, partner_ids=partner_ids, number_field=number_field,
                sms_numbers=sms_numbers, sms_pid_to_number=sms_pid_to_number, **kwargs
            )

