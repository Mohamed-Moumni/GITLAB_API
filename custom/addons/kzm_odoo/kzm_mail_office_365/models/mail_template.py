# -*- coding: utf-8 -*-

import logging
from odoo import models
from odoo.tools import formataddr

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, email_layout_xmlid=False):
        email_values['email_from'] = formataddr((self.env.company.name, self.env.company.email or self.env.user.email))
        email_values['email_to'] = formataddr((self.env.user.employee_id.name, self.env.user.employee_id.email))
        return super(MailTemplate, self).send_mail(res_id, force_send, raise_exception, email_values, email_layout_xmlid)






