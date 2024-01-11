# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    x_id_ext = fields.Char(string="ID Externe RPC")
