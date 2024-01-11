# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ClientHrEmloyee(models.Model):
    _name = 'client.hr.employee'
    _description = 'Client Hr Employee'

    name = fields.Char()
    id_ext = fields.Integer()
    database_metadata_id = fields.Many2one('database.metadata')