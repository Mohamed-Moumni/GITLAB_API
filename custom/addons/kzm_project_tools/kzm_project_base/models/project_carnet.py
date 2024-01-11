# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProjectCarnet(models.Model):
    _name = 'project.carnet'
    _description = 'Project Carnet'

    name = fields.Char(string=_("Name"), required=1)
    partner_id = fields.Many2one('res.partner', string="Client", domain=[('customer_rank', '>', 0)], required=1,
                                 readonly=1)
    contract_id = fields.Many2one('contract.cadre', string=_("Contract Cadre"), required=1, readonly=1,
                                  domain="['|',('customer_id', '=', partner_id),"
                                         "('secondary_customer_ids', 'in', partner_id)]")
    first_date = fields.Date(string=_("Start date"), required=1)
    last_date = fields.Date(string=_("Last date"), required=1)
    capacity = fields.Float(string=_("Capacity"), readonly=1)
    consumed = fields.Float(string=_("Consumed"))
    remaining = fields.Float(string=_("Remaining"))
    sale_id = fields.Many2one('sale.order', string=_("Order"), readonly=1)
    sale_line_id = fields.Many2one('sale.order.line', string=_("Order Line"), readonly=1)
    state = fields.Selection([
        ("new", "New"),
        ("in_progress", "In progress"),
        ("expired", "Expired")],
        string=_("State"),
        default="new", )
    project_id = fields.Many2one('project.project', string=_("Project"), readonly=1)
    task_id = fields.Many2one('project.task', string=_("Task"))
    default_code = fields.Char(string=_("Default Code"))
    desc = fields.Text(string="Description")

    @api.onchange('first_date', 'last_date')
    def check_values(self):
        for r in self:
            if r.first_date and r.last_date and r.first_date > r.last_date:
                raise ValidationError(_("first date should be smaller than last date"))

    def validate_method(self):
        for r in self:
            if r.state == 'new':
                r.state = 'in_progress'
                tache = False
                if r.state == 'in_progress':
                    r.contract_id.write({'next_carnet': r.contract_id.next_carnet + 1})
                    print(r.partner_id.name, r.default_code, str(r.contract_id.next_carnet).zfill(2))
                    tache = self.env['project.task'].create({
                        'project_id': r.project_id.id,
                        'name': r.partner_id.name + ("/" + r.default_code if r.default_code else "") + "/" + str(
                            r.contract_id.next_carnet).zfill(2),
                        'type': 'carnet',
                        'partner_id': r.partner_id.id,
                        'contract_id': r.contract_id.id,
                        'sale_order_id': r.sale_id.id,
                        'sale_line_id': r.sale_line_id.id,
                        'carnet_id': r._origin.id,
                        'planned_hours': r.capacity,
                    })
                if tache:
                    r.task_id = tache
                    # r.contract_id.product_owner = tache.user_ids[0].id

    def cancel_method(self):
        for r in self:
            if r.state == 'in_progress':
                r.state = 'expired'
                if r.task_id:
                    r.task_id.kanban_state = 'blocked'
                else:
                    print("no tasks related")
