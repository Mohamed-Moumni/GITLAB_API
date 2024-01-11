# -*- coding: utf-8 -*-
"""Import"""
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    """ Project Task """
    _inherit = 'project.task'

    team_id = fields.Many2one('helpdesk.team')
    timesheets_count = fields.Integer(compute="_compute_timesheets_count")
    activities_count = fields.Integer(compute="_compute_activities_count")
    ressources_count = fields.Integer(compute="_compute_ressources_count")
    reports_count = fields.Integer(compute="_compute_reports_count")
    task_consumption_ids = fields.One2many("task.consumption", 'task_id')

    def _compute_reports_count(self):
        for record in self:
            record.reports_count = len(record.task_consumption_ids)

    def reports_sm_action_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Reports"),
            'res_model': 'task.consumption',
            'domain': [('task_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {'default_task_id': self.id},
            'target': 'current',
        }

    def _compute_ressources_count(self):
        for record in self:
            ressources = self.env['planning.slot'].search([('task_id', '=', record.id)])
            record.ressources_count = len(ressources)

    def ressources_sm_action_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Ressources"),
            'res_model': 'planning.slot',
            'domain': [('task_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {'default_task_id': self.id},
            'target': 'current',
        }

    def _compute_activities_count(self):
        for record in self:
            activities = self.env['planification.line'].search([('task_id', '=', record.id)])
            record.activities_count = len(activities)

    def activities_sm_action_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Activities"),
            'res_model': 'planification.line',
            'domain': [('task_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {'default_task_id': self.id},
            'target': 'current',
        }

    @api.depends('timesheet_ids')
    def _compute_timesheets_count(self):
        for record in self:
            record.timesheets_count = len(record.timesheet_ids)

    def timesheets_sm_action_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Timesheets"),
            'res_model': 'account.analytic.line',
            'domain': [('id', 'in', self.timesheet_ids.ids)],
            'view_mode': 'tree,form',
            'context': {'default_task_id': self.id},
            'target': 'current',
        }
