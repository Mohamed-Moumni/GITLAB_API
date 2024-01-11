# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    x_id_ext = fields.Char(string="ID Externe RPC")
