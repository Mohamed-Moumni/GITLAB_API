# -*- coding: utf-8 -*-
"""Import"""
from odoo import models, fields, api, _


class PlanificationActivityLine(models.Model):
    """ Planification Activity Line """
    _name = 'planification.activity.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: _('New'))
    activity_id = fields.Many2one('planification.line', ondelete='cascade')
    task_id = fields.Many2one('project.task', compute="_compute_activity_fields", store=True, string='Tâche')
    team_id = fields.Many2one('helpdesk.team', compute="_compute_activity_fields", store=True, string='Équipe')
    partner_id = fields.Many2one('res.partner', compute="_compute_activity_fields", store=True, string='Client')
    ticket_id = fields.Many2one('helpdesk.ticket')
    ticket_stage_id = fields.Many2one('helpdesk.stage', related="ticket_id.stage_id")
    description = fields.Char()
    ressources_ids = fields.One2many('planning.slot', 'plan_id', ondelete='cascade')
    total_charge = fields.Float('Charge totale', compute='_compute_charge_totale', store="True")
    activity_id_task_id = fields.Many2one(related="activity_id.task_id")

    @api.onchange('ticket_id')
    def _check_ticket_id(self):
        for record in self:
            record.description = record.ticket_id.name

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('planification.activity.line') or _('New')
        res = super(PlanificationActivityLine, self).create(vals)
        return res

    @api.depends('activity_id', 'activity_id.task_id', 'activity_id.team_id', 'activity_id.task_id.partner_id')
    def _compute_activity_fields(self):
        for record in self:
            if record.activity_id:
                record.task_id = record.activity_id.task_id.id
                record.team_id = record.activity_id.team_id.id
                record.partner_id = record.activity_id.task_id.partner_id.id

    @api.depends('ressources_ids', 'ressources_ids.allocated_hours')
    def _compute_charge_totale(self):
        for record in self:
            if record.ressources_ids:
                record.total_charge = sum(record.ressources_ids.mapped('allocated_hours'))
