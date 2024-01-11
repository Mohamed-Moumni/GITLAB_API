# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ProjectModule(models.Model):
    _name = 'project.module'
    _description = 'project module'

    name = fields.Char(string=_("Name"), required=1)
    tech_name = fields.Char(string=_("Technical name"), required=1)
    git_link = fields.Char(string=_("Git Link"), required=1)
    etiquette = fields.Many2many('module.tag', string=_("Etiquette"))
    version = fields.Many2many('odoo.version', string=_("Version"))
