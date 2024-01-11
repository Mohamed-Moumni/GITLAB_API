# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    contract_id = fields.Many2one('contract.cadre', string=_("Contract Cadre"), readonly=1,
                                  compute="_get_contract_cadre", store=1)

    @api.depends('order_ids')
    def _get_contract_cadre(self):
        for r in self:
            if r.order_ids:
                for o in r.order_ids:
                    if o.contract_id:
                        r.contract_id = o.contract_id.id
                        break
                if not r.contract_id:
                    r.contract_id = False
            else:
                r.contract_id = False

    def action_set_won_rainbowman(self):
        if self.partner_id and self.contract_id and self.order_ids:
            validated = False
            for r in self.order_ids:
                if r.contract_id and r.state in ['sale', 'done']:
                    validated = True
                    break
            if validated:
                super(CrmLead, self).action_set_won_rainbowman()
            else:
                raise ValidationError(_("The linked quote is not validated"))
        elif not self.partner_id:
            raise ValidationError(_("Please choose/create a customer"))
        elif not self.order_ids:
            raise ValidationError(_("Quote is not linked"))
        elif not self.contract_id:
            raise ValidationError(_("Please choose the framework contract on the linked quote"))
