# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api

MODULE_TO_INSTALL = ['base_setup', 'kzm_duplicate_base_safe', 'kzm_database_cleanup', 'hr_employee_firstname',
                     'auto_backup']


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _get_module(self, name):
        return self.env['ir.module.module'].sudo().search([('name', '=', name), ('state', '=', 'uninstalled')])

    @api.model
    def install_base_setup(self):
        for module_name in MODULE_TO_INSTALL:
            module = self._get_module(module_name)
            if module:
                module.sudo().button_install()
