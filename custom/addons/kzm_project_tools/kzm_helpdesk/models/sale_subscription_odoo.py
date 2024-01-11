
from odoo import models, fields, api


class SaleSubscriptionOdoo(models.Model):
    _name = 'sale.subscription.odoo'
    _description = 'Subscription Odoo Version'

    name = fields.Char(string="Version")