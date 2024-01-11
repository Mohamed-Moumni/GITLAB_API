# -*- coding: utf-8 -*-
"""Import"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class TaskConsumption(models.Model):
    """ Task Consumption """
    _name = "task.consumption"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "task_id"

    @api.model
    def _default_start_date(self):
        if self.env.context.get('default_task_id'):
            task = self.env['project.task'].browse(self.env.context.get('default_task_id'))
            tickets = task.ticket_ids.sorted()
            if tickets:
                return tickets[-1].create_date

    @api.model
    def _default_end_date(self):
        if self.env.context.get('default_task_id'):
            task = self.env['project.task'].browse(self.env.context.get('default_task_id'))
            tickets = task.ticket_ids.sorted()
            if tickets:
                return tickets[0].create_date

    start_date = fields.Date(default=_default_start_date)
    end_date = fields.Date(default=_default_end_date)
    task_id = fields.Many2one('project.task', tracking=True)
    consumption_line_ids = fields.One2many('task.consumption.line', 'task_consumption_id', string="Report lines")
    report_lines_count = fields.Integer(compute="_compute_report_lines_count")

    @api.constrains('start_date', 'end_date')
    def _check_start_date_and_end_date_for_controle(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError(_("End date must be greater than or equal to start date"))

    @api.depends('consumption_line_ids')
    def _compute_report_lines_count(self):
        for record in self:
            record.report_lines_count = len(record.consumption_line_ids)

    def action_report_lines_sm_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Report lines"),
            'res_model': 'task.consumption.line',
            'domain': [('id', 'in', self.consumption_line_ids.ids)],
            'view_mode': 'tree',
            'view_id': self.env.ref('kzm_planning.taks_consumption_line_list_view').id,
            'context': {'default_task_consumption_id': self.id},
            'target': 'current',
        }

    @api.constrains('start_date', 'end_date')
    def _check_start_date_and_end_date_for_controle(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError(_("End date must be greater than or equal to start date"))

    @api.constrains('start_date', 'end_date', 'task_id')
    def _check_start_date_and_end_date(self):
        for record in self:
            record.consumption_line_ids.unlink()
            if record.start_date and record.end_date:
                if record.task_id:
                    tickets = record.task_id.ticket_ids.filtered(
                        lambda element: record.start_date <= element.create_date.date() <= record.end_date)
                    for rec in tickets:
                        record.consumption_line_ids = [
                            (0, 0, {'created_on': rec.create_date, 'ticket_id': int(rec.id), 'subject': rec.name,
                                    'type_id': rec.ticket_type_id.id, 'estimated_charge': rec.estimated_charge,
                                    'state': rec.stage_id.id})]
