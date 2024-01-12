from odoo import models,fields


"""
    Database Server Model
"""

class DatabaseServer(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    _name = "database.server"
    _description = "Class for Database Server"
    
    name = fields.Char('Name')
    ip = fields.Char('Ip')
    region = fields.Char('Region')