# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ContratCadre(models.Model):
    _name = 'contract.cadre'
    _inherit = 'mail.thread'
    _description = 'Contrat Cadre'

    name = fields.Char(string=_("Name"), required=1)
    customer_id = fields.Many2one('res.partner', string=_("Client"))
    first_date = fields.Date(string=_("Start date"), tracking=True)
    last_date = fields.Date(string=_("Last date"), tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("actif", "Actif"),
        ("resilie", "Terminated")],
        string=_("State"),
        default="draft", tracking=True)
    secondary_customer_ids = fields.One2many('res.partner', 'contract_cadre_id', string=_("Secondary customers"))
    contact_ids = fields.One2many('res.partner', 'contract_cadre_id_contact', string=_("Contacts"),
                                  compute="_get_contacts",
                                  store=True)
    next_carnet = fields.Integer(default=0, string=_("Notebook Number"))
    next_abbo = fields.Integer(default=0, string=_("Subscription Number"))
    next_project = fields.Integer(default=0, string=_("Project Number"))

    lead_ids = fields.One2many('crm.lead', 'contract_id', string=_("Leads"))
    leads_count = fields.Integer(compute="_elements_count", string=_("Number of Leads"))

    subscription_ids = fields.One2many('sale.order', 'contract_id', domain=[('is_subscription', '=', True)],
                                       string="Subscriptions")
    subscription_count = fields.Integer(compute="_elements_count", string=_("Subscription Number"))

    carnet_ids = fields.One2many('project.carnet', 'contract_id', string=_("Notebook"))
    carnet_count = fields.Integer(compute="_elements_count", string=_("Notebook Number"))

    task_ids = fields.One2many('project.task', 'contract_id', string=_("Tasks"))
    task_count = fields.Integer(compute="_elements_count", string=_("Tasks Number"))

    order_ids = fields.One2many('sale.order', 'contract_id', string=_("Orders"))
    order_count = fields.Integer(compute="_elements_count", string=_("Orders Number"))

    move_ids = fields.One2many('account.move', 'contract_id', string=_("Moves"))
    move_count = fields.Integer(compute="_elements_count", string=_("Moves Number"))

    project_ids = fields.One2many('project.project', 'contract_id', string=_("Projects"))
    project_count = fields.Integer(compute="_elements_count", string=_("Projects Number"))

    ticket_ids = fields.One2many('helpdesk.ticket', 'contract_id', string=_("Tickets"))
    ticket_count = fields.Integer(compute="_elements_count", string=_("tickets Number"))

    timesheet_ids = fields.One2many('account.analytic.line', 'contract_id', string=_("Timesheet"))
    timesheet_count = fields.Integer(compute="_elements_count", string=_("Number of Timesheet"))

    database_ids = fields.One2many('project.database', 'contract_id', string=_("Databases"))
    database_count = fields.Integer(compute="_elements_count", string=_("Number of Databases"))
    # task_request_count = fields.Integer(compute="_elements_count", string=_("Number of task request"))
    sold_derogation_count = fields.Integer(compute="_elements_count", string=_("Number of sold derogation"))

    ressource_affectation_ids = fields.One2many('affectation.ressource', 'contract_id', string=_("Resources"))
    resource_affectation_count = fields.Integer(compute="_elements_count",
                                                 string=_("Number des affectations resources"))

    tag = fields.Many2one('contract.tag', string='Tag')
    responsable = fields.Many2one('res.users', string='Responsible', required=True,
                                  domain=lambda self: [("groups_id", "=",
                                                        self.env.ref("base.group_user").id)])
    product_owner = fields.Many2one('res.users', string='Product Owner', required=True,
                                    domain=lambda self: [("groups_id", "=",
                                                          self.env.ref("base.group_user").id)])
    team_lead = fields.Many2one('res.users', string='Team Lead', required=True, domain=lambda self: [("groups_id", "=",
                                                                                                      self.env.ref(
                                                                                                          "base.group_user").id)])

    @api.depends('lead_ids', 'subscription_ids', 'carnet_ids', 'order_ids', 'move_ids', 'project_ids',
                 'ressource_affectation_ids')
    def _elements_count(self):
        for r in self:
            tasks = self.env['project.task'].search([('contract_id', '=', self.id)])
            # tasks_request = self.env['task.request'].search([('contract_id', '=', self.id)])
            sold_derogation = self.env['sold.task.derogation'].search([('contract_id', '=', self.id)])
            r.leads_count = len(r.lead_ids) if r.lead_ids else 0
            r.subscription_count = len(r.subscription_ids) if r.subscription_ids else 0
            r.carnet_count = len(r.carnet_ids) if r.carnet_ids else 0
            r.task_count = len(tasks)
            # r.task_request_count = len(tasks_request)
            r.sold_derogation_count = len(sold_derogation)
            r.order_count = len(r.order_ids) if r.order_ids else 0
            r.move_count = len(r.move_ids) if r.move_ids else 0
            r.project_count = len(r.project_ids) if r.project_ids else 0
            r.ticket_count = len(r.ticket_ids) if r.ticket_ids else 0
            r.timesheet_count = len(r.timesheet_ids) if r.timesheet_ids else 0
            r.database_count = len(r.database_ids) if r.database_ids else 0
            r.resource_affectation_count = len(r.ressource_affectation_ids) if r.ressource_affectation_ids else 0

    def get_leads(self):
        return {
            "name": _("Leads"),
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.lead_ids.ids)],
            "context": {"default_partner_id": self.customer_id.id, "default_contract_id": self.id},
        }

    def get_subscription(self):
        return {
            "name": _("Subscriptions"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.subscription_ids.ids)],
            "context": {"default_contract_id": self.id, "default_partner_id": self.customer_id.id,
                        "default_is_subscription": True},
        }

    def get_carnet(self):
        return {
            "name": _("Notebooks"),
            "type": "ir.actions.act_window",
            "res_model": "project.carnet",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.carnet_ids.ids)],
            "context": {"default_contract_id": self.id},
        }

    # def get_task_request(self):
    #     return {
    #         "name": _("Task requests"),
    #         "type": "ir.actions.act_window",
    #         "res_model": "task.request",
    #         "view_mode": "tree,form",
    #         "domain": [("contract_id", "=", self.id)],
    #         "context": {"default_contract_id": self.id},
    #     }

    def get_sold_derogation(self):
        return {
            "name": _("Sold derogation"),
            "type": "ir.actions.act_window",
            "res_model": "sold.task.derogation",
            "view_mode": "tree,form",
            "domain": [("contract_id", "=", self.id)],
            "context": {"default_contract_id": self.id},
        }

    def get_tasks(self):
        return {
            "name": _("Tasks"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "tree,form",
            "domain": [("contract_id", "=", self.id)],
            "context": {"default_contract_id": self.id},
        }

    def get_orders(self):
        return {
            "name": _("Orders"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "tree,form",
            "domain": [("contract_id", "=", self.id)],
            "context": {"default_partner_id": self.customer_id.id, "default_contract_id": self.id},
        }

    def get_invoices(self):
        return {
            "name": _("Invoices"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": [("contract_id", "=", self.id)],
            "context": {"default_contract_id": self.id},
        }

    def get_projects(self):
        return {
            "name": _("Projects"),
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "view_mode": "tree,form",
            "domain": [("contract_id", "=", self.id)],
            "context": {"default_contract_id": self.id},
        }

    def get_tickets(self):
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

    def get_databases(self):
        return {
            "name": _("Database"),
            "type": "ir.actions.act_window",
            "res_model": "project.database",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.database_ids.ids)],
            "context": {"default_client": self.customer_id.id, "default_contract_id": self.id},
        }

    def get_resources(self):
        return {
            "name": _("Affectation resources"),
            "type": "ir.actions.act_window",
            "res_model": "affectation.ressource",
            "view_mode": "tree,search",
            "domain": [("id", "in", self.ressource_affectation_ids.ids)],
            "context": {"default_contract_id": self.id},
        }

    @api.depends('customer_id', 'secondary_customer_ids', 'secondary_customer_ids.child_ids', 'customer_id.child_ids')
    def _get_contacts(self):
        for r in self:
            child_ids = r.customer_id.child_ids.ids + r.secondary_customer_ids.child_ids.ids
            r.contact_ids = self.env["res.partner"].search([('id', 'in', child_ids)])

    @api.onchange('first_date', 'last_date')
    def check_values(self):
        for r in self:
            if r.first_date and r.last_date and r.first_date > r.last_date:
                raise ValidationError(_("first date should be smaller than last date"))

    def unlink(self):
        if self.subscription_count >= 1 or self.project_count >= 1:
            raise ValidationError("You cannot delete a contract order with a linked order or project!")
        return super(ContratCadre, self).unlink()
