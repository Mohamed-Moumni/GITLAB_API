# -*- coding: utf-8 -*-

import datetime

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TeamLineEval(models.Model):
    _name = 'project.team.line.eval'

    name = fields.Char('Name', compute='_compute_name')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    mean_note = fields.Float('Project Mean note', compute='_compute_note')
    team_availability = fields.Float("Team availability", compute='_compute_team_availability')
    project_id = fields.Many2one('project.project', 'Project', required=True)

    @api.depends('employee_id', 'project_id')
    def _compute_name(self):
        for o in self:
            o.name = str(o.employee_id and o.employee_id.name or '-') + ':' + str(
                o.project_id and o.project_id.name or '-')

    @api.depends('employee_id', 'project_id')
    def _compute_note(self):
        for o in self:
            o.mean_note = 0
            if o.employee_id and o.project_id:
                evals = self.env['kzm.hr.evaluation.eval'].search(
                    [('employe_id', '=', o.employee_id.id), ('project_id', '=', o.project_id.id)])
                note_mean = sum([l.mean_note for l in evals])
                o.mean_note = note_mean / (len(evals) or 1)

    @api.depends('employee_id')
    def _compute_team_availability(self):
        for o in self:
            o.team_availability = 0
            if o.employee_id:
                date_now = datetime.datetime.now()
                date_90d = date_now + datetime.timedelta(days=90)
                number_weeks = date_90d.isocalendar()[1] - date_now.isocalendar()[1]
                days_dispo = number_weeks * o.employee_id.days_week_works
                days_conge_fere = 0
                holidays = self.env['hr.leave'].search([('employee_id', '=', o.employee_id.id)])
                # set HH:MM:SS to 00:00:00 in date_now and 23:59:59 in date_end !!! comment
                free_all = holidays.filtered(
                    lambda r: r.date_from and r.date_to and r.date_from >= str(date_now) and r.date_to <= str(date_90d))
                nb_free_all = sum([l.number_of_days_temp for l in free_all])
                for l in (holidays - free_all):
                    if not (l.date_from and l.date_to):
                        continue
                    date_st = datetime.datetime.strptime(str(l.date_from), DEFAULT_SERVER_DATETIME_FORMAT)
                    date_ot = datetime.datetime.strptime(str(l.date_to), DEFAULT_SERVER_DATETIME_FORMAT)
                    while date_st < date_ot:
                        if date_now <= date_st <= date_90d:
                            nb_free_all += 1
                        date_st = date_st + datetime.timedelta(days=1)
                o.team_availability = max(days_dispo - days_conge_fere - nb_free_all, 0)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    hr_modele_id = fields.Many2one('kzm.hr.modele.eval', 'Evaluation Model')
    hr_evaluation_ids = fields.One2many('kzm.hr.evaluation.eval', 'project_id',
                                        string='Evaluations')  # domain model eval
    team_line_ids = fields.One2many('project.team.line.eval', 'project_id', string='Team projects')
    mean_note_team = fields.Float("Mean note team", compute='_compute_mean_note')
    nb_evaluations = fields.Integer("Nbr Evaluations", compute='_compute_nbs')
    nb_team_line = fields.Integer("Nbr project teams", compute='_compute_nbs')

    @api.depends('hr_evaluation_ids', 'team_line_ids')
    def _compute_nbs(self):
        for o in self:
            o.nb_evaluations = len(o.hr_evaluation_ids)
            o.nb_team_line = len(o.team_line_ids)

    @api.depends('team_line_ids')
    def _compute_mean_note(self):
        for o in self:
            notes = [l.mean_note for l in o.team_line_ids]
            o.mean_note_team = float(sum(notes)) / (len(notes) or 1.0)


class KzmEvaluation(models.Model):
    _inherit = 'kzm.hr.evaluation.eval'

    project_id = fields.Many2one('project.project', 'Project', related="task_id.project_id", store=True)
    task_id = fields.Many2one('project.task', 'Task')

    @api.onchange('project_id')
    def on_change_project_id(self):
        for o in self:
            if o.project_id.hr_modele_id:
                o.hr_modele_id = o.project_id.hr_modele_id
            else:
                o.hr_modele_id = False


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    plan_evaluation_ids = fields.One2many('kzm.hr.plan.evaluation.eval', 'employe_id', 'Periodic plan evaluations')
    days_week_works = fields.Float('Days works / Week', default=5)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.depends('hr_evaluation_ids')
    def _get_evol_counts(self):
        for o in self:
            o.evolutions_count = len(o.hr_evaluation_ids)

    hr_evaluation_ids = fields.One2many('kzm.hr.evaluation.eval', 'task_id',
                                        string='Evaluations')
    evolutions_count = fields.Float('Evolution count', compute=_get_evol_counts)
