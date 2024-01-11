from odoo import exceptions
from odoo.tests import common

class TestHrEmployee(common.SingleTransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestHrEmployee, self).setUp(*args, **kwargs)
        admin_user = self.env.ref('base.user_admin')
        self.hr_employee = self.env['hr.employee'].with_user(admin_user)
        self.kzm_instance_request = self.env['kzm.instance.request'].with_user(admin_user)
        self.kzm_instance_request0 = self.kzm_instance_request.create({})
        self.hr_employee0 = self.hr_employee.create({
            'cpu': 'Intel Core I11',
            'ram': '128GB',
            'disk': '2TB',
            'url': 'www.hello.com',
            'state': 'Soumise',
            ''
        })
        
