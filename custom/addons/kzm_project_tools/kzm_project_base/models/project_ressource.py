# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class ProjectRessource(models.Model):
    _name = 'project.ressource'
    _description = 'project ressource'

    name = fields.Char(string=_("Name"), required=1)
    description = fields.Char(string=_("Description"), required=1)
    # client_ids = fields.Many2many('res.partner', compute="_get_clients", string=_("Client"),
    #                               domain=[('customer_rank', '>', 0)])

    client_id = fields.Many2one('res.partner', string=_("Client"), domain=[('customer_rank', '>', 0)])
    contract_id = fields.Many2one('contract.cadre', string=_("Contract"))
    contract_count = fields.Integer(compute="_get_count", string=_("Nombres des contrats"))
    client_count = fields.Integer(compute="_get_count", string=_("Nombres des clients"))
    cost = fields.Float(string=_("Coût"))
    # contract_ids = fields.Many2many('contract.cadre', string=_("Contract"),
    #                               domain="['|',('customer_id', '=', client), ('secondary_customer_ids', 'in', client)]")
    type = fields.Many2one('ressource.type', string="Type")

    @api.onchange('client_id')
    def contrat_domain(self):
        for r in self:
            if r.client_id != r.contract_id.customer_id and r.client_id not in r.contract_id.secondary_customer_ids:
                r.contract_id = False

    def _get_count(self):
        for r in self:
            r.client_count = len(r.client_ids) if r.client_ids else 0
            r.contract_count = len(r.contract_ids) if r.contract_ids else 0

    def contracts_SM(self):
        return {
            "name": _("Contrat cadre"),
            "type": "ir.actions.act_window",
            "res_model": "contract.cadre",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.contract_ids.ids)],
            "context": {"default_ressource_ids": [self.id]},
        }

    def clients_SM(self):
        return {
            "name": _("Clients"),
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.client_ids.ids)],
            "context": {"default_ressource_ids": [self.id]},
        }
