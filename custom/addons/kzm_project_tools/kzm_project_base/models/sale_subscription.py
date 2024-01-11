# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class SaleSubscription(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one('contract.cadre', string=_("Contract Cadre"),
                                  domain="['|',('customer_id', '=', partner_id),('secondary_customer_ids', 'in', partner_id)]")

    project_id = fields.Many2one('project.project', string=_("Project"))
    task_id = fields.Many2one('project.task', string=_("Task"))
    sale_id = fields.Many2one('sale.order', string=_("Order"), readonly=1)
    date = fields.Date(string="Start de fin")
    timesheet_ids = fields.One2many(related="task_id.timesheet_ids", string="Feuilles de temps")
    timesheet_count = fields.Integer(compute="_get_cont", string="Nombres des feuilles de temps")
    ticket_ids = fields.One2many(related="task_id.ticket_ids", string="Tickets")
    ticket_count = fields.Integer(compute="_get_cont", string="Nombres des Tickets")
    default_code = fields.Char(string="Code par defaut")

    @api.depends('timesheet_ids', 'ticket_ids')
    def _get_cont(self):
        for r in self:
            r.ticket_count = len(r.ticket_ids) if r.ticket_ids else 0
            r.timesheet_count = len(r.timesheet_ids) if r.timesheet_ids else 0

    def set_close(self):
        super(SaleSubscription, self).set_close()
        if self.stage_id.category == 'closed' and self.task_id:
            self.task_id.kanban_state = 'blocked'

    def get_ticket(self):
        return {
            "name": _("Tickets"),
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.ticket_ids.ids)],
            "context": {"default_contract_id": self.id},
        }

    def get_timesheet(self):
        return {
            "name": _("Time sheets"),
            "type": "ir.actions.act_window",
            "res_model": "account.analytic.line",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.timesheet_ids.ids)],
            "context": {"default_contract_id": self.id},
        }


class SaleSubscriptionModel(models.Model):
    _inherit = 'sale.order.template'

    is_model = fields.Boolean(string=_("Is model"), store=1)
