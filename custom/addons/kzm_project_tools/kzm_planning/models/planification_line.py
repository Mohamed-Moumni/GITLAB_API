# -*- coding: utf-8 -*-
"""Import"""
from datetime import date
from odoo import models, fields, api, _


class PlanificationLine(models.Model):
    """ Planification Line """
    _name = 'planification.line'
    _rec_name = 'task_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: _('New'))
    task_id = fields.Many2one('project.task')
    team_id = fields.Many2one('helpdesk.team', related='task_id.team_id', store=True)
    contract_id = fields.Many2one('contract.cadre', string="Master agreement")
    assign_to_ids = fields.Many2many('res.users', compute='_compute_assign_to_ids', store=True)
    plafond = fields.Float(related='task_id.plafond', store=True)
    planned_hours = fields.Float(related='task_id.planned_hours', string="Allocated H", store=True)
    effective_hours = fields.Float(related='task_id.effective_hours', string="Past H", store=True)
    remaining_hours = fields.Float(related='task_id.remaining_hours', string="Remaining H", store=True)
    capacity = fields.Float(compute="_compute_capacity", store=True)
    planification_id = fields.Many2one('planification.planification', ondelete='cascade')
    description = fields.Html()
    estimated_charge = fields.Float(compute="_compute_estimated_charge", store=True)
    real_charge = fields.Float(compute="_compute_real_charge", string="Realized charge", store=True)
    difference = fields.Float(compute="_compute_difference", store=True)
    to_plan = fields.Boolean()
    state = fields.Selection(
        [('draft', 'Brouillon'), ('finished', 'À approuver'), ('approved', 'Approuvé'), ('cancelled', 'Annulé')],
        default='draft')
    planning_ids = fields.One2many('planification.activity.line', 'activity_id', string="Lignes de planification",
                                   ondelete='cascade')
    tickets_count = fields.Integer(compute="_compute_tickets_count")
    ressources_count = fields.Integer(compute="_compute_ressources_count")
    planned_ticket_ids = fields.Many2many('helpdesk.ticket', compute="_compute_planned_ticket_ids")
    not_planned_ticket_ids = fields.Many2many('helpdesk.ticket', compute="_compute_not_planned_ticket_ids")
    planned_ticket_ids_count = fields.Integer(compute="_compute_planned_ticket_ids_count",
                                              string="Number of planned tickets")
    not_planned_ticket_ids_count = fields.Integer(compute="_compute_not_planned_ticket_ids_count",
                                                  string="Number of unplanned tickets")
    estimated_charge_not_planned = fields.Float(compute="_compute_estimated_charge_not_planned")
    estimated_charge_planned = fields.Float(compute="_compute_estimated_charge_planned")
    real_charge_planned = fields.Float(compute="_compute_real_charge_planned")
    real_charge_not_planned = fields.Float(compute="_compute_real_charge_not_planned")
    scrum_master_id = fields.Many2one('res.users')

    @api.depends('not_planned_ticket_ids')
    def _compute_real_charge_not_planned(self):
        for record in self:
            record.real_charge_not_planned = sum(record.not_planned_ticket_ids.mapped('real_charge'))

    @api.depends('planned_ticket_ids')
    def _compute_real_charge_planned(self):
        for record in self:
            record.real_charge_planned = sum(record.planned_ticket_ids.mapped('real_charge'))

    @api.depends('planned_ticket_ids')
    def _compute_estimated_charge_planned(self):
        for record in self:
            record.estimated_charge_planned = sum(record.planned_ticket_ids.mapped('estimated_charge'))

    @api.depends('not_planned_ticket_ids')
    def _compute_estimated_charge_not_planned(self):
        for record in self:
            record.estimated_charge_not_planned = sum(record.not_planned_ticket_ids.mapped('estimated_charge'))

    @api.depends('not_planned_ticket_ids')
    def _compute_not_planned_ticket_ids_count(self):
        for record in self:
            record.not_planned_ticket_ids_count = len(record.not_planned_ticket_ids.ids)

    @api.depends('planned_ticket_ids')
    def _compute_planned_ticket_ids_count(self):
        for record in self:
            record.planned_ticket_ids_count = len(record.planned_ticket_ids.ids)

    def _compute_not_planned_ticket_ids(self):
        for record in self:
            tickets = self.env['helpdesk.ticket'].search([('create_date', '>=', record.planification_id.first_date),
                                                          ('create_date', '<=', record.planification_id.last_date),
                                                          ('task_id', '=', record.task_id.id),
                                                          ('track_ids', '=', False)])
            record.not_planned_ticket_ids = tickets

    def _compute_planned_ticket_ids(self):
        for record in self:
            record.planned_ticket_ids = False
            tickets = self.env['helpdesk.ticket'].search([('task_id', '=', record.task_id.id)])
            if tickets:
                tickets_filtres = tickets.filtered(
                    lambda element: record.planification_id.id in element.track_ids.mapped('planification_id').ids)
                record.planned_ticket_ids = tickets_filtres

    def ressources_sm_action_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Ressources"),
            'res_model': 'planning.slot',
            'domain': [('id', 'in', self.planning_ids.mapped('ressources_ids').ids)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def _compute_ressources_count(self):
        for record in self:
            ressources = record.planning_ids.mapped('ressources_ids').ids
            record.ressources_count = len(ressources)

    @api.depends('task_id')
    def _compute_tickets_count(self):
        for record in self:
            record.tickets_count = self.env['helpdesk.ticket'].search_count(
                [('task_id', '=', record.task_id.id), ('stage_id.is_clotured', '=', False)])

    def action_tickets(self):
        tickets = self.env['helpdesk.ticket'].search([('task_id', '=', self.task_id.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': "Tickets",
            'res_model': 'helpdesk.ticket',
            'domain': [('id', 'in', tickets.ids), ('stage_id.is_clotured', '=', False)],
            'context': {'default_task_id': self.task_id.id,
                        'default_partner_id': self.task_id.partner_id.id,
                        'default_team_id': self.team_id.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def prepare_values_to_create(self):
        today_date = date.today()
        return {'type': 'Sold_increase', 'task_id': self.task_id.id,
                'contract_id': self.task_id.contract_id.id,
                'estimated_time': abs(self.difference) + self.planned_hours - self.plafond,
                'user_id': self.env.user.id, 'date': today_date,
                'pattern': self.description, 'state': 'on_hold'}

    def approve_planification_line(self):
        for record in self:
            record.state = 'approved'
            if record.difference < 0:
                if abs(record.difference) + record.planned_hours <= record.plafond:
                    record.task_id.planned_hours += abs(record.difference)
                if (abs(record.difference) + record.planned_hours) > record.plafond:
                    record.task_id.planned_hours = record.plafond
                    values = record.prepare_values_to_create()
                    self.env['sold.task.derogation'].create(values)

    def refuse_planification_line(self):
        for record in self:
            record.state = 'cancelled'

    @api.depends('task_id', 'task_id.timesheet_ids', 'task_id.timesheet_ids.date')
    def _compute_real_charge(self):
        for record in self:
            account_analytic_lines = self.env['account.analytic.line'].search(
                [('task_id', '=', record.task_id.id), ('date', '>=', record.planification_id.first_date),
                 ('date', '<=', record.planification_id.last_date)])
            record.real_charge = sum(account_analytic_lines.mapped('unit_amount'))

    def valider_planification_line(self):
        for record in self:
            record.state = 'finished'

    def reset_to_draft(self):
        for record in self:
            record.state = 'draft'

    @api.depends('task_id')
    def _compute_assign_to_ids(self):
        for record in self:
            record.assign_to_ids = record.task_id.user_ids

    @api.depends('remaining_hours', 'estimated_charge')
    def _compute_difference(self):
        for record in self:
            record.difference = record.remaining_hours - record.estimated_charge

    @api.depends('planning_ids', 'planning_ids.ressources_ids', 'planning_ids.ressources_ids.allocated_hours')
    def _compute_estimated_charge(self):
        for record in self:
            charge = sum(record.planning_ids.ressources_ids.mapped('allocated_hours'))
            record.estimated_charge = charge

    @api.depends('plafond', 'effective_hours')
    def _compute_capacity(self):
        for record in self:
            record.capacity = record.plafond - record.effective_hours

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('planification.line.increment') or _('New')
        res = super(PlanificationLine, self).create(vals)
        return res
