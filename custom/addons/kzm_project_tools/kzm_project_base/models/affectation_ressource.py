# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class AffectationResource(models.Model):
    _name = 'affectation.ressource'
    _description = 'Affectation resource'
    client_id = fields.Many2one('res.partner', string=_("Client"), domain=[('customer_rank', '>', 0)])
    ressource_id = fields.Many2one('project.ressource', string=_("Resource"))
    ressource_domain = fields.Many2many('project.ressource', compute="_get_domain", string=_("Resource domain"))
    contract_id = fields.Many2one('contract.cadre', string=_("Contract"))
    first_date = fields.Date(string=_("Affectation date"), required=1)
    last_date = fields.Date(string=_("Termination date"), required=1)

    @api.depends('client_id')
    def _get_domain(self):
        for r in self:
            domain = []
            if r.client_id:
                domain = [('client_id', '=', r.client_id.id)]
            resource = self.env['project.ressource'].sudo().search(domain)
            if resource:
                r.ressource_domain = resource.ids
            else:
                r.ressource_domain = False
