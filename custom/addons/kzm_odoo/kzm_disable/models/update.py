from odoo import api, fields, models
from datetime import datetime


class PublisherWarrantyContractInherit(models.Model):
    _name = 'kzm.disable'

    @api.model
    def update_notification(self):

        cron = self.env['ir.cron'].sudo().search([('id', '=', 3)])
        if cron:
            cron.write({'active': False})

        set_param = self.env['ir.config_parameter'].sudo().set_param
        new_expiration_date = datetime(2030, 10, 10)
        formatted_date = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
        existing_expiration_date = self.env['ir.config_parameter'].sudo().get_param('database.expiration_date')
        #if existing_expiration_date:
        set_param('database.expiration_date', formatted_date)

        return True
