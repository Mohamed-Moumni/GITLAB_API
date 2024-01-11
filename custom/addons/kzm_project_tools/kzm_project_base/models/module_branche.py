# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ModuleBranch(models.Model):
    _name = 'module.branche'
    _description = 'module des branches'
    name = fields.Char(string=_("Name"), required=1)
    git_link = fields.Char(string=_("Git Link"), required=1)
    version = fields.Many2one('odoo.version', string=_("Version"))
    dependance_ids = fields.Many2many(
        comodel_name='module.branche',
        relation='module_branch_rel',
        column1='src_id',
        column2='dest_id',
        string="Branch", domain="[('id', '!=', active_id),('version','=',version)]")

