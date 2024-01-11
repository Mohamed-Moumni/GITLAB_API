# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AffectTicketWizard(models.TransientModel):
    _name = 'affectation.ticket.wizard'

    domain_tickets = fields.Many2many('helpdesk.ticket',string="Tickets", compute="_get_domain",)
    ticket_id = fields.Many2one('helpdesk.ticket',string="Ticket")
    new_ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")

    @api.depends('ticket_id','ticket_id.contract_id')
    def _get_domain(self):
        for r in self:
            domain = []
            if r.ticket_id:
                domain = [('contract_id', '=', r.ticket_id.contract_id.id),('id','!=',r.ticket_id.id)]
            tickets = self.env['helpdesk.ticket'].search(domain)
            if tickets:
                r.domain_tickets = tickets.ids
            else:
                r.domain_tickets = False

    def affect_ticket(self):
        timesheets = self.env['account.analytic.line'].search([('helpdesk_ticket_id', '=', self.ticket_id.id)])
        if self.new_ticket_id:
            for ts in timesheets:
                ts.write({'helpdesk_ticket_id':self.new_ticket_id.id,
                          'task_id':self.new_ticket_id.task_id.id,
                          'project_id': self.new_ticket_id.project_id.id,
                })


