# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    x_id_ext = fields.Char(string="ID Externe RPC")
