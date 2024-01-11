# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class AffectationModule(models.Model):
    _name = 'affectation.module'
    _description = 'Affectation module'
    module_id = fields.Many2one('project.module', string=_("Module"), required=1)
    database_id = fields.Many2one('project.database', string=_("Data base"))
    branch_id = fields.Many2one('module.branche', string=_("Branch"), required=1)
    domain_branch = fields.Many2many('module.branche', compute="_get_domain", string=_("Branch domain"))

    @api.depends('database_id')
    def _get_domain(self):
        for r in self:
            domain = []
            if r.database_id:
                domain = [('version', '=', r.database_id.version.id)]
            branch = self.env['module.branche'].search(domain)
            print("branch", branch, r.database_id.version)
            if branch:
                r.domain_branch = branch.ids
            else:
                r.domain_branch = False

