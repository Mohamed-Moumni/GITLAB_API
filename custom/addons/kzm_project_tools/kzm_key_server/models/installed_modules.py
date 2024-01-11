# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class InstalledModules(models.Model):
    _name = 'installed.modules'
    _description = 'Installed Modules'

    name = fields.Char()
    version = fields.Char()
    dependencies = fields.Text()
    path = fields.Char()
    database_metadata_id = fields.Many2one('database.metadata')
