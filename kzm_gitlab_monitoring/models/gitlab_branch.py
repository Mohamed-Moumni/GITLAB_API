from odoo import models, fields, api, exceptions


class GilabBranch(models.Model):
    _name = "gitlab.branch"
    _description = "Gitlab Branch"

    name = fields.Char('Branch Name')
    project_ids = fields.One2many('project.database', 'branch_id')
    
    
    
