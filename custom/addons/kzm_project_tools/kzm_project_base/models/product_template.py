# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    type_1 = fields.Selection([
        ("carnet", "Carnet"),
        ("autre", "Autre")],
        string=_("Type"))

    service_type_ids = fields.Many2one('service.type', string="Type de service")
