# -*- coding: utf-8 -*-
"""Import"""
from odoo import models, fields


class TrackPlaning(models.Model):
    """ Track Planing """
    _name = 'track.planing'

    planification_id = fields.Many2one('planification.planification')
    first_date = fields.Date(string="Date début")
    last_date = fields.Date(string="Date fin")
    ticket_id = fields.Many2one('helpdesk.ticket')
