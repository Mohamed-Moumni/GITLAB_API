# -*- coding: utf-8 -*-
"""Import"""
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PlanificationPlanification(models.Model):
    """ Planification Planification """
    _name = 'planification.planification'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: _('New'))
    first_date = fields.Date(string="Start date", required=True)
    last_date = fields.Date(string="End date", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('validated', 'Validated')], default="draft")
    plan = fields.One2many('planification.line', 'planification_id', ondelete='cascade')
    plan_line_count = fields.Integer(compute="_compute_plan_line_count")
    planning_count = fields.Integer(compute="_compute_planning_count")
    slot_count = fields.Integer(compute="_compute_slot_count")
    planned_ticket_count = fields.Integer(string="Number of planned tickets", compute="_compute_planned_ticket_count")
    not_planned_ticket_count = fields.Integer(compute="_compute_not_planned_ticket_count",
                                              string="Number of unplanned tickets")
    estimated_charge_not_planned = fields.Float(compute="_compute_estimated_charge_not_planned")
    estimated_charge_planned = fields.Float(compute="_compute_estimated_charge_planned")
    real_charge_planned = fields.Float(compute="_compute_real_charge_planned")
    real_charge_not_planned = fields.Float(compute="_compute_real_charge_not_planned")

    @api.depends('plan', 'plan.real_charge_not_planned')
    def _compute_real_charge_not_planned(self):
        for record in self:
            record.real_charge_not_planned = sum(record.plan.mapped('real_charge_not_planned'))

    @api.depends('plan', 'plan.real_charge_planned')
    def _compute_real_charge_planned(self):
        for record in self:
            record.real_charge_planned = sum(record.plan.mapped('real_charge_planned'))

    @api.depends('plan', 'plan.estimated_charge_planned')
    def _compute_estimated_charge_planned(self):
        for record in self:
            record.estimated_charge_planned = sum(record.plan.mapped('estimated_charge_planned'))

    @api.depends('plan', 'plan.estimated_charge_not_planned')
    def _compute_estimated_charge_not_planned(self):
        for record in self:
            record.estimated_charge_not_planned = sum(record.plan.mapped('estimated_charge_not_planned'))

    @api.depends('plan', 'plan.not_planned_ticket_ids')
    def _compute_not_planned_ticket_count(self):
        for record in self:
            record.not_planned_ticket_count = sum(record.plan.mapped('not_planned_ticket_ids_count'))

    @api.depends('plan', 'plan.planned_ticket_ids')
    def _compute_planned_ticket_count(self):
        for record in self:
            record.planned_ticket_count = sum(record.plan.mapped('planned_ticket_ids_count'))

    def _create_planification_by_cron(self):
        today = datetime.today()
        monday_offset = (0 - today.weekday() + 7) % 7
        closest_monday = today + timedelta(days=monday_offset)
        closest_friday = closest_monday + timedelta(days=4)
        planification_exists = self.env['planification.planification'].search(
            [('first_date', '=', closest_monday), ('last_date', '=', closest_friday)])
        if not planification_exists:
            self.env['planification.planification'].create({
                'first_date': closest_monday.date(),
                'last_date': closest_friday.date()
            })

    @api.depends("plan.planning_ids")
    def _compute_planning_count(self):
        for record in self:
            record.planning_count = len(record.plan.planning_ids)

    @api.depends("plan.planning_ids", "plan.planning_ids.ressources_ids")
    def _compute_slot_count(self):
        for record in self:
            record.slot_count = len(record.plan.planning_ids.ressources_ids)

    def action_planning(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "Lignes planification",
            'res_model': 'planification.activity.line',
            'domain': [('id', 'in', self.plan.planning_ids.ids)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_slot(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "Ressources",
            'res_model': 'planning.slot',
            'domain': [('id', 'in', self.plan.planning_ids.ressources_ids.ids)],
            'view_mode': 'gantt,tree,form,kanban,pivot,graph',
            'target': 'current',
        }

    @api.depends("plan")
    def _compute_plan_line_count(self):
        for record in self:
            record.plan_line_count = len(record.plan)

    def action_plan_line(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "Activités",
            'res_model': 'planification.line',
            'domain': [('id', 'in', self.plan.ids)],
            'view_mode': 'tree,form',
            'context': {'default_planification_id': self.id},
            'target': 'current',
        }

    def generate_tasks(self):
        for record in self:
            record.plan.unlink()
            tasks = self.env['project.task'].search([('stage_id.is_progress', '=', True)])
            for rec in tasks:
                values = {'task_id': rec.id, 'contract_id': rec.contract_id.id}
                plan = self.env['planification.line'].create(values)
                record.plan = [(4, plan.id)]

    def update_tasks(self):
        for record in self:
            plan_tasks = self.plan.mapped('task_id')
            tasks = self.env['project.task'].search([('stage_id.is_progress', '=', True),
                                                     ('id', 'not in', plan_tasks.ids)])
            for rec in tasks:
                values = {'task_id': rec.id,
                          'contract_id': rec.contract_id.id,
                          'planification_id': record.id}
                self.env['planification.line'].create(values)

            closed_plan_tasks = self.plan.filtered(lambda o: o.task_id.stage_id.is_progress is False or not o.task_id)
            if closed_plan_tasks:
                closed_plan_tasks.unlink()

    @api.constrains("first_date")
    def _check_first_date(self):
        for record in self:
            if record.first_date > record.last_date:
                raise ValidationError(_('The start date must be less than the end date.'))

    def remettre_en_brouillon(self):
        for record in self:
            tracking_lines = self.env['track.planing'].sudo().search([('planification_id', '=', self.id)])
            tracking_lines.sudo().unlink()
            record.state = 'draft'

    def valider(self):
        for record in self:
            for planning in self.plan.planning_ids:
                self.env['track.planing'].sudo().create({
                    'planification_id': self.id,
                    'first_date': self.first_date,
                    'last_date': self.last_date,
                    'ticket_id': planning.ticket_id.id,
                })
            record.state = 'validated'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('planification.planification.increment') or _('New')
        res = super(PlanificationPlanification, self).create(vals)
        return res
