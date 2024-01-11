# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    google_auth_api_folder = fields.Char("Auth file")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_auth_api_folder = fields.Char(related='company_id.google_auth_api_folder', store=1, readonly=False)
