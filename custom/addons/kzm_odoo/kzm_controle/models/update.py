from odoo import api, fields, models
from datetime import datetime


class PublisherWarrantyContractInherit(models.Model):
    _name = 'kzm.update.data'

    @api.model
    def update_notification(self):

        set_param = self.env['ir.config_parameter'].sudo().set_param
        new_expiration_date = datetime(2030, 10, 10)
        formatted_date = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
        #set_param('database.expiration_date', formatted_date)
        set_param('kzm.number', 10)
        set_param('kzm.number_active', 10)
        set_param('kzm.number_share', 10)
        set_param('kzm.number_active_share', 10)
        return True
