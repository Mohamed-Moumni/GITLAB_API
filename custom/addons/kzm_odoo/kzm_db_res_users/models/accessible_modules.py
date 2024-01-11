# -*- coding: utf-8 -*-
from odoo import models, fields


class AccessibleModules(models.Model):
    _name = 'accessible.modules'
    _description = 'Accessible Modules'

    name = fields.Char()
    module_type = fields.Selection(
        [("leave", "Congés"),
         ("note_frais", "Note de Frais"),
         ("timesheet", "Feuille de temps"),
         ("admin_rh", "Admin RH")],

        help="Choose the module.",
    )
    id_ext = fields.Integer()
    color = fields.Integer()
