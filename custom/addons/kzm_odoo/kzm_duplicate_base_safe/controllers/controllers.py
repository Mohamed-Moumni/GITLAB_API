# -*- coding: utf-8 -*-

from odoo import api, registry, SUPERUSER_ID
from odoo import http
from odoo.addons.web.controllers.database import Database


class KzmDatabase(Database):

    @http.route('/web/database/duplicate', type='http', auth="none", methods=['POST'],
                csrf=False)
    def duplicate(self, master_pwd, name, new_name):
        res = super(KzmDatabase, self).duplicate(master_pwd, name, new_name)
        with registry(new_name).cursor() as new_cr:
            env = api.Environment(new_cr, SUPERUSER_ID, {})
            env['ir.cron'].search([]).write({'active': False})
            env['ir.mail_server'].search([]).write({'active': False})
            back_up = env['ir.model'].search([('model', '=', 'db.backup')])
            if back_up:
                env['db.backup'].search([]).unlink()
        return res
