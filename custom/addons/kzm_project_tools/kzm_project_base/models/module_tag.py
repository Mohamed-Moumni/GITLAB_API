# -*- coding: utf-8 -*-
from random import randint

from odoo import fields, models, _


class ModuleTag(models.Model):
    _name = 'module.tag'
    _description = 'module tag'
    name = fields.Char(string=_("Name"), required=1)

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(default=_get_default_color)
