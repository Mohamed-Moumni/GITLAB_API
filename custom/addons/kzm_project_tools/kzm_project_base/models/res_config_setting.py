# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    subscription_id = fields.Many2one(related="company_id.subscription_id",
                                      string=_("Subscription"), readonly=False, required=1)
    carnet_id = fields.Many2one(related="company_id.carnet_id",
                                string=_("Carnet"), readonly=False, required=1)
    show_real_charge_portal = fields.Boolean(string="Afficher Charge réelle (Portail)",
                                             related="company_id.show_real_charge_portal", readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'
    subscription_id = fields.Many2one('project.project', string=_("Subscription"))
    carnet_id = fields.Many2one('project.project', string=_("Carnet"))
    show_real_charge_portal = fields.Boolean(string="Afficher Charge réelle (Portail)")
