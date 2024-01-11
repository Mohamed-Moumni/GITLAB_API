# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class DbResUsers(models.Model):
    _name = 'db.res.users'
    _description = 'Database Users'

    name = fields.Char()
    login = fields.Char()
    id_ext = fields.Integer()
    is_active = fields.Boolean(default=True)
    user_create_date = fields.Datetime()
    is_mobile = fields.Boolean(default=True)
    key_licence = fields.Char(default="TEST")
    activation_date = fields.Datetime(default=fields.Datetime.now)
    expiration_date = fields.Datetime(compute='_compute_expiration_date', inverse='_inverse_expiration_date')
    modules_accessible = fields.Selection(
        [("leave", "Congés"),
         ("note_frais", "Note de Frais"),
         ("timesheet", "Feuille de temps")],

        help="Choose the module.",
    )
    accessible_modules_ids = fields.Many2many('accessible.modules')
    used = fields.Boolean()

    @api.onchange('activation_date')
    def _compute_expiration_date(self):
        for rec in self:
            if rec.activation_date:
                rec.expiration_date = rec.activation_date + relativedelta(years=1)
            else:
                rec.expiration_date = datetime.datetime.today()

    def _inverse_expiration_date(self):
        pass
