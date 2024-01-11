# -*- coding: utf-8 -*-
"""Import"""
import datetime
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PlanningSlot(models.Model):
    """ Planning Slot """
    _inherit = 'planning.slot'

    task_id = fields.Many2one('project.task', related="plan_id.task_id", store=True)
    ticket_id = fields.Many2one('helpdesk.ticket', related="plan_id.ticket_id", store=True)
    team_id = fields.Many2one('helpdesk.team', related="plan_id.team_id", store=True)
    description = fields.Char(required=True)
    state = fields.Selection(selection='get_state_selection_option', string='Status', default='')
    priority = fields.Selection([
        ('0', 'Low priority'), ('1', 'Medium priority'),
        ('2', 'High priority'), ('3', 'Urgent')], default='0', tracking=True)
    project_id = fields.Many2one('project.project', related="task_id.project_id")
    plan_id = fields.Many2one('planification.activity.line', ondelete='cascade')
    date = fields.Date(required=True)
    allocated_hours = fields.Float("Charge", compute='_compute_allocated_hours', store=True, readonly=False)
    member_ids = fields.Many2many('resource.resource', compute="_compute_member_ids")

    @api.onchange("date")
    def _tester_date(self):
        for record in self:
            if record.date and (
                    record.date > record.plan_id.activity_id.planification_id.last_date or record.date < record.plan_id.activity_id.planification_id.first_date):
                raise ValidationError(_('The date must be between the planning start and end dates.'))

    def get_state_selection_option(self):
        return [('progress', 'En cours'), ('treated', 'Traité'), ('deferred_int', 'Reporté Int'),
                ('deferred_clt', 'Reporté Clt')]

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(PlanningSlot, self).default_get(fields_list)
    #     res['start_datetime'] = ''
    #     res['end_datetime'] = ''
    #     return res

    @api.depends('allocated_hours', 'date', 'start_datetime')
    def _compute_datetime(self):
        for rec in self:
            if rec.date:
                rec.start_datetime = datetime.datetime.strptime(str(rec.date) + " 07:00:00", "%Y-%m-%d %H:%M:%S")
            if rec.start_datetime and rec.allocated_hours:
                rec.end_datetime = rec.start_datetime + timedelta(hours=rec.allocated_hours)

    @api.depends('team_id', 'team_id.member_ids')
    def _compute_member_ids(self):
        for rec in self:
            employee_ids = rec.team_id.member_ids.employee_ids
            resources = self.env['resource.resource'].search([('employee_id', 'in', employee_ids.ids)])
            rec.member_ids = resources.ids

    @api.depends(
        'start_datetime', 'end_datetime', 'resource_id.calendar_id',
        'company_id.resource_calendar_id', 'allocated_percentage', 'resource_id.flexible_hours')
    def _compute_allocated_hours(self):
        pass
