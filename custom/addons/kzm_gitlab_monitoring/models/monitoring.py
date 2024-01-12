from odoo import fields, models

"""
    Monitoring model class for postgresql server
"""

class Monitoring(models.Model):
    _inherit = "project.database"
    _description = "Monitoring Postgresql Server"
    
    ssl_expiration_date = fields.Date('SSL Expiration Date')
    disk_usage = fields.Char('Disk Usage')
    ip = fields.Char('Postgresql server IP')
    
    
    def monitor_synch(self):
        pass