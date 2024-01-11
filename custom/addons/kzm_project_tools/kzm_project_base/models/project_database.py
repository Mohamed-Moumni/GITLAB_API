# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProjectDatabase(models.Model):
    _name = 'project.database'
    _description = 'project database'
    name = fields.Char(string=_("Name"), required=1)
    client = fields.Many2one('res.partner', string=_("Client"), domain=[('customer_rank', '>', 0)], required=1)
    contract_id = fields.Many2one('contract.cadre', string=_("Contract"),
                                  domain="['|',('customer_id', '=', client), ('secondary_customer_ids', 'in', client)]")
    position = fields.Selection([
        ("test", "Test"),
        ("preprod", "Préprod"),
        ("prod", "Prod")],
        string=_("Position"),
        default="test")
    link = fields.Char(string=_("Link"))
    first_date = fields.Date(string=_("First date of activation"))
    expiration_date = fields.Date(string=_("Expiration date"))
    version = fields.Many2one('odoo.version', string=_("Version"))
    backup_ids = fields.One2many('kzm.backup.tracker.gantt', 'data_base', string=_("backups"))
    affectation_module_ids = fields.One2many('affectation.module', 'database_id', string=_("Affectations"))
    backup_count = fields.Integer(compute='get_backup_num', string=_("Nombres des backups"))

    def get_backup_num(self):
        for r in self:
            r.backup_count = len(r.backup_ids) if r.backup_ids else 0

    @api.onchange('client')
    def _resent_contract(self):
        if self.client:
            contract = self.env['contract.cadre'].search(
                ['|', ('customer_id', '=', self.client.id), ('secondary_customer_ids', 'in', self.client.id)])
            contr_dict = {}
            if contract:
                for sec in contract:
                    if sec.first_date in contr_dict.keys():
                        contr_dict[sec.first_date] |= sec
                    else:
                        contr_dict[sec.first_date] = sec
                first_contract = [x for x in sorted(contr_dict.keys())]
                self.contract_id = contr_dict[first_contract[-1]][0]
            else:
                self.contract_id = False
        else:
            self.contract_id = False

    def get_backup_ids(self):
        return {
            "name": _("Backups"),
            "type": "ir.actions.act_window",
            "res_model": "kzm.backup.tracker.gantt",
            "view_mode": "gantt,tree,form",
            "domain": [("id", "in", self.backup_ids.ids)],
            "context": {"default_data_base": self.id},
        }
