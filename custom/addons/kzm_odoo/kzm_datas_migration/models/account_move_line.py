# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    x_id_ext = fields.Char(string="ID Externe RPC")
    old_ref_lettrage = fields.Char("Ancien référence de lettrage")



