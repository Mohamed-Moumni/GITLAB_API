# -*- coding: utf-8 -*-

from odoo import fields, models, _


class OdooVersion(models.Model):
    _name = 'odoo.version'
    _description = 'odoo version'
    name = fields.Char(string=_("Name"), required=1)
