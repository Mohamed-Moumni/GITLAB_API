from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    instances_ids = fields.One2many('kzm.instance.request', 'sale_order_id', string="Instances Request")

    @api.model
    def action_create_instance(self,vals):
        view_id = self.env.ref('kzm_instance_request.view_create_instances_wizard_form').id
        return {
            'name': 'Instance creation',
            'type': 'ir.actions.act_window',
            'res_model': 'create.instances.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_sale_order_ids': vals},
        }