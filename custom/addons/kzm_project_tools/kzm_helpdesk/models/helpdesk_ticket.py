# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelpdeskTicketType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    description = fields.Text(string="Description")


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    contact = fields.Many2one('res.partner', string="Contact")
    subscription_id = fields.Many2one('sale.subscription', "Subscription")
    validity_date = fields.Date(string="Validity Date", related='subscription_id.recurring_next_date')
    nature_id = fields.Many2one('helpdesk.ticket.type', "Nature")
    available_sold = fields.Float("Available Solde")
    sla_ticket = fields.Float("Sla Ticket")
    nature_ids = fields.Many2many('helpdesk.ticket.type', string="Natures", store=True, compute='get_nature_ids')
    odoo_version_id  = fields.Many2one('sale.subscription.odoo', string="Odoo Version", related='subscription_id.odoo_version_id')

    @api.model
    def create(self, vals):
        if vals.get('subscription_id'):
            subscription = self.env['sale.subscription'].search([('id', '=', vals['subscription_id'])])
            vals['user_id'] = subscription.teamlead_id.id

        res = super(HelpdeskTicket, self).create(vals)
        return res

    @api.depends('subscription_id')
    def get_nature_ids(self):
        for rec in self:
            tags = []
            for serv in rec.subscription_id.service_ids:
                for tag in serv.tag_ids:
                    if tag.id in tags:
                        pass
                    else:
                        tags.append(tag.id)
            natures = []
            for nature in rec.subscription_id.service_ids:
                if nature.type_id.id in natures:
                    pass
                else:
                    natures.append(nature.type_id.id)
            rec.tag_ids = [(6, 0, tags)]
            rec.nature_ids = [(6, 0, natures)]

    @api.onchange('partner_id')
    def set_nature(self):
        subsciptions = self.env['sale.subscription'].search([])
        for sub in subsciptions:
            if sub.partner_id.id == self.partner_id.id:
                self.subscription_id = sub.id
                break
