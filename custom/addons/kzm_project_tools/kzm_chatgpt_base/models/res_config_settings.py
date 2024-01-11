# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openai_api_key = fields.Text(string="API key", related="company_id.openai_api_key", readonly=False)
    openai_model = fields.Text(string="Model", related="company_id.openai_model", readonly=False)
    custom_openai_model = fields.Many2one('chatgpt.model', string="Custom Model", related="company_id.custom_openai_model", readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    openai_api_key = fields.Text(string="API key")
    openai_model = fields.Text(string="Model")
    custom_openai_model = fields.Many2one('chatgpt.model', string="Custom Model", domain=[('state', '=', 'succeeded')])
