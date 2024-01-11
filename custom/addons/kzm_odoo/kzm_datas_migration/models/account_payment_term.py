# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    x_id_ext = fields.Char(string="ID Externe RPC")
