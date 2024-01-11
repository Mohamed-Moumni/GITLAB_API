from odoo import models, fields, api


class OdooVersion(models.Model):
    _name = 'odoo.version'
    _description = 'Versions of Odoo'

    name = fields.Char(
        string="Version",
        requried=True,
    )
    
    instance_ids = fields.One2many(
        'kzm.instance.request', 'odoo_id', string="Instance Request")

    instance_nums = fields.Integer(
        string="Number of Instance Request", compute="compute_instance_nums")
    
    quotations = fields.One2many('sale.order', 'version_odoo_id', string="quotations")

    @api.depends('instance_ids')
    def compute_instance_nums(self):
        instance_nums = len(self.instance_ids)
        return instance_nums