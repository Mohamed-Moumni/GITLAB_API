# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ContratTag(models.Model):
    _name = 'contract.tag'
    _description = 'contract tag'

    name = fields.Char(required=True, string="Nom")
