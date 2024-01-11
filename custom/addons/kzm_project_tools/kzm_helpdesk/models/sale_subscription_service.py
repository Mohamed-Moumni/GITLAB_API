# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleSubscriptionService(models.Model):
    _name = 'sale.subscription.service'
    _description = 'Subscription Service'

    subscription_id = fields.Many2one('sale.subscription', string="Subscription")
    service_id = fields.Many2one('product.product', string="Service", domain=[('recurring_invoice', '=', True)])
    type_id = fields.Many2one('helpdesk.ticket.type', string="Type")
    sla_average_id = fields.Many2one('helpdesk.sla', string="SLA Average")
    tag_ids = fields.Many2many('helpdesk.tag', string="Tags")

    # @api.onchange('services')
    # def _get_type(self):
    #     return {'domain': {'type': [('ticket_type_id', 'in', self.type.id)]}}

    @api.onchange('type_id')
    def _get_sla_average(self):
        return {'domain': {'sla_average_id': [('ticket_type_id', '=', self.type_id.id)]}}

    @api.onchange('subscription_id')
    def _get_type(self):
        return {'domain': {'type_id': [('ticket_type_id', 'in',
                                        self.service_id.operation_id.ids)]}}
