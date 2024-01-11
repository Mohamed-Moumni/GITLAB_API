# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    x_id_ext = fields.Char(string="ID Externe RPC")
