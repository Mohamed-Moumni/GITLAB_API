# -*- coding: utf-8 -*-
from odoo import models, fields


class DbResUsers(models.Model):
    _inherit = "db.res.users"

    employee_ids = fields.Many2one('hr.employee', string='Employé')
    res_user_id = fields.Many2one('res.users')
    client_user_id = fields.Integer(related='res_user_id.id')


