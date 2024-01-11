# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    tel = fields.Char("Tel number")
    copied_to = fields.Char("Copied To")



