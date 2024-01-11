# -*- coding: utf-8 -*-
"""Import"""
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    """ Track Planing """
    _inherit = 'helpdesk.ticket'

    track_ids = fields.One2many('track.planing', 'ticket_id', ondelete='cascade')
    is_estimated_charge_readonly = fields.Boolean(string="Is estimated charge")
    ticket_derogations_count = fields.Integer(compute="_compute_ticket_derogations_count")
    is_not_planned = fields.Boolean()
    is_planned = fields.Boolean()
    is_late = fields.Boolean()
    track_ids_count = fields.Integer(compute="_compute_track_ids_count", store=True)

    @api.depends('track_ids')
    def _compute_track_ids_count(self):
        for record in self:
            record.track_ids_count = len(record.track_ids.ids)

    @api.constrains('track_ids_count', 'stage_id')
    def _check_track_ids(self):
        for record in self:
            if not record.stage_id.is_clotured:
                if not record.track_ids:
                    record.is_not_planned = True
                    record.is_planned = record.is_late = False
                elif record.track_ids:
                    retard = record.track_ids.filtered(
                        lambda rec: fields.Date.today() > rec.last_date)
                    if retard:
                        record.is_late = True
                        record.is_not_planned = record.is_planned = False
                    else:
                        record.is_late = record.is_not_planned = False
                        record.is_planned = True

    def _compute_ticket_derogations_count(self):
        for record in self:
            derogations = self.env['sold.ticket.derogation'].search([('ticket_id', '=', record.id)])
            record.ticket_derogations_count = len(derogations.ids)

    def action_ticket_derogations_sm_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Ticket Derogation"),
            'res_model': 'sold.ticket.derogation',
            'domain': [('ticket_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {'default_ticket_id': self.id, 'default_existing_charge': self.estimated_charge},
            'target': 'current',
        }

    @api.constrains('estimated_charge')
    def _check_estimated_charge_for_is_estimated_charge_readonly(self):
        for record in self:
            if record.estimated_charge > 0:
                record.is_estimated_charge_readonly = True
            else:
                record.is_estimated_charge_readonly = False

    # @api.onchange('estimated_charge', 'task_id', 'task_id.plafond', 'task_id.plafond')
    # def check_estimated_charge(self):
    #     for rec in self:
    #         if rec.estimated_charge > rec.task_id.plafond - rec.task_id.effective_hours:
    #             raise ValidationError(_("The estimated workload exceeds the available ceiling."))

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('id', operator, name)]

        return self._search(expression.AND([domain, args]),
                            limit=limit, access_rights_uid=name_get_uid)

    def copy(self, default=None):
        res = super().copy(default)
        res.is_estimated_charge_readonly = False
        return res
