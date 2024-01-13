from odoo import models,fields


"""
    Database Server Model
"""

class DatabaseServer(models.Model):
    """
        Database Server model for project instance
    Args:
        models (_type_): _description_
    """
    _name = "database.server"
    _description = "Class for Database Server model"
    
    name = fields.Char('Name')
    ip = fields.Char('Ip')
    region = fields.Char('Region')