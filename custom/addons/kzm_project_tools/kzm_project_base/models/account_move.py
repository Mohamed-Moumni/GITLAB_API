# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one('contract.cadre', string=_("Contrat Cadre"), compute="_compute_contract_id"
                                  , store=True)
    
    @api.depends('partner_id')
    def _compute_contract_id(self):
        for rec in self:
            contract = False
            if rec.partner_id:
                contract = rec.env['contract.cadre'].sudo().search(
                    ['|', ('customer_id', '=', rec.partner_id.id), '|',
                     ('secondary_customer_ids', 'in', rec.partner_id.id),
                     ('contact_ids', 'in', rec.partner_id.id),
                     ], order='first_date DESC', limit=1
                )
            rec.contract_id = contract
    
