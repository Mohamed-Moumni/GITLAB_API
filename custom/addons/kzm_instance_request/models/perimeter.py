from odoo import models, fields

class perimeter(models.Model):
    _name = 'perimeter.perimeter'
    _description = 'perimeter object'
    
    name = fields.Char(string="perimeter", required=True)