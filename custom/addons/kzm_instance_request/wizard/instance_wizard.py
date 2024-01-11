from odoo import models, fields, api


class CreateInstancesWizard(models.TransientModel):
    _name = 'create.instances.wizard'
    _description = 'Create Instances Wizard'

    sale_order_ids = fields.Many2many(
        'sale.order', string='sale Order')
    tl_id = fields.Many2one('hr.employee', string='employee')
    cpu = fields.Char(string='CPU')
    ram = fields.Char(string='RAM')
    disk = fields.Char(string='Disk')

    def create_instances(self):
        for s_order in self.sale_order_ids:
            instance_data = {'sale_order_id': s_order.id, 'cpu': self.cpu,
                             'ram': self.ram, 'disk': self.disk, 'tl_id': self.tl_id.id, }
            self.env['kzm.instance.request'].create(instance_data)
        return {
            'name': 'kzm.instance.request.view',
            'type': 'ir.actions.act_window',
            'res_model': 'kzm.instance.request',
            'view_mode': 'tree',
            'view_id': self.env.ref('kzm_instance_request.kzm_instance_request_view').id,
        }
