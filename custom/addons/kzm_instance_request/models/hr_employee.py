from odoo import models, fields, api


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    instance_ids = fields.One2many(
        'kzm.instance.request', 'tl_id', string="Instance Request")
    instance_nums = fields.Integer(
        string="Number of Instance Request", compute="compute_instance_nums")
    
    @api.depends('instance_ids')
    def compute_instance_nums(self):
        instance_nums = len(self.instance_ids)
        return instance_nums
    
    def action_show_instances(self):
        action = self.env.ref('kzm_instance_request.action_view_instance').read()[0]
        action['context'] = {'default_employee_id': self.id}
        return action
    