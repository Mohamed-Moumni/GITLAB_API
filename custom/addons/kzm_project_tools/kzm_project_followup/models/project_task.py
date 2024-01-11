# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    type = fields.Selection([
        ('normal', 'Normal'),
        ('action', 'Action'),
    ], required=False, default='normal',)

    project_action_id = fields.Many2one('project.project', String="Project", required=True)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    task_ids = fields.One2many('project.task', 'project_action_id', string="Actions", domain=[('type','=','action')])



