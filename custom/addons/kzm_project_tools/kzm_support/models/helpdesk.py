# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.depends('timesheet_ids.unit_amount')
    def _compute_real_charges(self):
        for o in self:
            o.real_charge = sum([l.unit_amount for l in o.timesheet_ids])

    contract_state = fields.Selection([
        ('out', 'Out of contract'),
        ('under', 'Under contract')
    ], string='Contract state')

    estimated_charge = fields.Float("Estimated Charge")
    real_charge = fields.Float("Real Charge",compute=_compute_real_charges,store=True)




