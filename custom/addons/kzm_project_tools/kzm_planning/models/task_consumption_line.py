# -*- coding: utf-8 -*-
"""Import"""
from odoo import models, fields


class TaskConsumptionLine(models.Model):
    """ Task Consumption Line """
    _name = 'task.consumption.line'

    created_on = fields.Date()
    ticket_id = fields.Integer(string="ID")
    subject = fields.Char()
    type_id = fields.Many2one('helpdesk.ticket.type')
    estimated_charge = fields.Float()
    state = fields.Many2one('helpdesk.stage')
    task_consumption_id = fields.Many2one('task.consumption', string="Report", ondelete="cascade")
