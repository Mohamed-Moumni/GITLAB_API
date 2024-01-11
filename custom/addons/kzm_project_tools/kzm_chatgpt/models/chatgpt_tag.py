from odoo import api, fields, models


class ChatgptTag(models.Model):
    _name = 'chatgpt.tag'
    _description = 'chatgpt.tag'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")
