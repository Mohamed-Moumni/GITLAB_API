# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    db_res_user_id = fields.One2many('db.res.users', 'res_user_id')
    is_mobile_user = fields.Boolean('Est un utilisateur mobile')
