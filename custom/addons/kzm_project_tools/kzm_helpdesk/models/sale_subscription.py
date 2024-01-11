# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    project_id = fields.Many2one('project.project', string="Project")
    task_id = fields.Many2one('project.task', string="Task")
    service_ids = fields.One2many('sale.subscription.service', 'subscription_id', string="Service", ondelete="cascade")
    teamlead_id = fields.Many2one('res.users', string="Teamlead")
    odoo_version_id  = fields.Many2one('sale.subscription.odoo', string="Odoo Version")

    @api.model
    def create(self, vals):
        project = self.env['project.project'].search([('company_id', '=', vals['company_id'])])
        vals['project_id'] = project.id
        customer = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
        task = self.env['project.task'].create({
            'name': customer.name + ' ' + vals['code'],
            'project_id': project.id,
        })
        vals['task_id'] = task.id
        res = super(SaleSubscription, self).create(vals)
        return res


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    consumed_load = fields.Float(string="Consumed Load", compute='set_consumed_load')

    def set_consumed_load(self):
        for rec in self:
            tickets = self.env['helpdesk.ticket'].search([('nature_id','=',rec.product_id.operation_id.id)])
            sum=0
            for ticket in tickets:
                for time_sh  in ticket.timesheet_ids:
                    sum+=time_sh.unit_amount

            rec.consumed_load=sum




