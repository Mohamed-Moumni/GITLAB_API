# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    min_tokens = fields.Integer(string="Min Tokens", related="company_id.min_tokens", readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    min_tokens = fields.Integer(string="Min Tokens")
