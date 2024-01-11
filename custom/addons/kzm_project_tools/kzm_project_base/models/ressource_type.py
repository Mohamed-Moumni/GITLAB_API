# -*- coding: utf-8 -*-

from odoo import fields, models, _


class RessourceType(models.Model):
    _name = 'ressource.type'
    _description = 'resource type'

    name = fields.Char(string=_("Name"), required=1)
