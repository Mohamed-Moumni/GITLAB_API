# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ServiceType(models.Model):
    _name = 'service.type'
    _description = 'service type'

    name = fields.Char(string=_("Name"), required=1)
