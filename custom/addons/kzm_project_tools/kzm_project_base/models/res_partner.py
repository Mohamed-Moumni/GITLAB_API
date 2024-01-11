from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_cadre_id = fields.Many2one('contract.cadre', string="champs inverse pour les clients secondaire")
    contract_cadre_id_contact = fields.Many2one('contract.cadre', string="Champs inverse pour les contacts")
    customer_rank = fields.Integer(default=0, copy=False, string="client rang")
    contract_ids = fields.One2many('contract.cadre', 'customer_id', string=_("Contracts"))
    contract_count = fields.Integer(compute="_get_counts", string="Nombre des contrats")
    carnet_ids = fields.One2many('project.carnet', 'partner_id', string=_("Carnets"))
    carnet_count = fields.Integer(compute="_get_counts", string="Nombre des carnets")
    project_ids = fields.One2many('project.project', 'partner_id', string=_("Projects"))
    project_count = fields.Integer(compute="_get_counts", string="Nombre des projets")

    database_ids = fields.One2many('project.database', 'client', string="Base de donnees")
    database_count = fields.Integer(compute="_elements_count", string="Nombre des bases de donnees")
    ice = fields.Char(string="ICE")

    def _get_counts(self):
        for r in self:
            r.contract_count = len(r.contract_ids) if r.contract_ids else 0
            r.carnet_count = len(r.carnet_ids) if r.carnet_ids else 0
            r.project_count = len(r.project_ids) if r.project_ids else 0
            r.database_count = len(r.database_ids) if r.database_ids else 0

    def get_contract(self):
        return {
            "name": _("Contracts"),
            "type": "ir.actions.act_window",
            "res_model": "contract.cadre",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.contract_ids.ids)],
            "context": {"default_customer_id": self.id},
        }

    def get_carnet(self):
        return {
            "name": _("Carnets"),
            "type": "ir.actions.act_window",
            "res_model": "project.carnet",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.carnet_ids.ids)],
            "context": {"default_partner_id": self.id},
        }

    def get_project(self):
        return {
            "name": _("Projects"),
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.project_ids.ids)],
            "context": {"default_partner_id": self.id},
        }

    def get_databases(self):
        return {
            "name": _("Database"),
            "type": "ir.actions.act_window",
            "res_model": "project.database",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.database_ids.ids)],
            "context": {"default_client": self.id},
        }

    def get_Ressources(self):
        return {
            "name": _("Ressources"),
            "type": "ir.actions.act_window",
            "res_model": "project.ressource",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.ressource_ids.ids)],
            "context": {"default_client_ids": [self.id]},
        }
