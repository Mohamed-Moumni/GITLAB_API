# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    x_id_ext = fields.Char(string="ID Externe RPC")
