# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ClientResUsers(models.Model):
    _name = 'client.res.users'
    _description = 'Client Res Users'

    name = fields.Char()
    id_ext = fields.Integer()
    is_mobile = fields.Boolean()
    database_metadata_id = fields.Many2one('database.metadata')