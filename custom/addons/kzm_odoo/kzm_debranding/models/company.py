# -*- coding: utf-8 -*-

from odoo import api, fields, models


class KzmResCompany(models.Model):
    _inherit = "res.company"

    background_image = fields.Binary(attachment=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    background_image = fields.Binary(related="company_id.background_image", readonly=False)

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(

            background_image=params.get_param('background_image'),
        )
        return res

    def set_values(self):
        super().set_values()
        config_parameter_sudo = self.env['ir.config_parameter'].sudo()
        config_parameter_sudo.set_param('background_image', self.background_image)
