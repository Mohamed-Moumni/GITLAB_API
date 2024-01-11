# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.AbstractModel):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string="Is a Customer?", compute="_compute_is_customer_supplier",
                                 inverse="_inverse_is_customer_supplier")
    is_supplier = fields.Boolean(string="Is a Supplier?", compute="_compute_is_customer_supplier",
                                 inverse="_inverse_is_customer_supplier")

    @api.depends('customer_rank', 'supplier_rank')
    def _compute_is_customer_supplier(self):
        for record in self:
            record.is_customer = True if record.customer_rank > 0 else False
            record.is_supplier = True if record.supplier_rank > 0 else False

    def _inverse_is_customer_supplier(self):
        for record in self:
            record.customer_rank = 1 if record.is_customer else 0
            record.supplier_rank = 1 if record.is_supplier else 0
