# -*- coding: utf-8 -*-

from odoo import models, fields


class l10n_ma_commune(models.Model):
    _name = "l10n.ma.commune"
    _description = 'Commune'

    name = fields.Char(string='Nom', size=64,  required=True)
    code = fields.Char(string='Code Commune', size=64,  required=True)
