# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_id_ext = fields.Char(string="ID Externe RPC")
