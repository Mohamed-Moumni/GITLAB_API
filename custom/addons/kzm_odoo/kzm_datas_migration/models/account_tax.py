# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountTax(models.Model):
    _inherit = "account.tax"

    x_id_ext = fields.Char(string="ID Externe RPC")


