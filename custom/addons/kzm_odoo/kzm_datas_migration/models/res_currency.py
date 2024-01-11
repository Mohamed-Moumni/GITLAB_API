# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCurrency(models.Model):
    _inherit = "res.currency"

    x_id_ext = fields.Char(string="ID Externe RPC")



