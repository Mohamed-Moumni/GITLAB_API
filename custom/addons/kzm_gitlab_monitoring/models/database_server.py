from odoo import models,fields,api,exceptions
import re
"""
    Database Server Model
"""

class DatabaseServer(models.Model):
    """
        Database Server model for project instance
    Args:
        models (models.Model): odoo ORM model
    """
    _name = "database.server"
    _description = "Class for Database Server model"
    
    _sql_constraints = [
        ('ip', 'unique(ip)', 'This ip address already Used')
    ]
    
    name = fields.Char('Name')
    ip = fields.Char('Ip', required=True)
    region = fields.Char('Region')
    
    @api.model
    def create(self, vals):
        if vals['ip'].lower() != "localhost":
            ip_address_pattern = r'^((25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})\.){3}(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})$'
            match = re.match(ip_address_pattern,vals['ip'])
            if not match:
                raise exceptions.UserError("Invalid Address IP")
        if not vals['name']:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'kzm_gitlab_monitoring.sequence')
        return super(DatabaseServer, self).create(vals)