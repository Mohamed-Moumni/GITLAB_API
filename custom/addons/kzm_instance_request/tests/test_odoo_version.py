from odoo import exceptions, fields
from odoo.tests import common
from datetime import datetime, timedelta

class TestOdooVersion(common.SingleTransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestOdooVersion, self).setUp(*args, **kwargs)
        admin_user = self.env.ref('base.user_admin')
        self.kzm_instance_request = self.env['kzm.instance.request'].with_user(
            admin_user)
        self.odoo_version = self.env['odoo.version'].with_user(
            admin_user)
    
    def test_compute_instance_nums(self):
        _odoo_version = self.odoo_version.create({
            'name':'16.0'
        })
        instance0 = self.kzm_instance_request.create({
            'cpu': 'Intel Core I7',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Soumise',
        })
        instance1 = self.kzm_instance_request.create({
            'cpu': 'Intel Core I9',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Soumise',
        })
        instance2 = self.kzm_instance_request.create({
            'cpu': 'Intel Core I11',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Soumise',
        })
        print(_odoo_version.id)
        instance0.odoo_id = _odoo_version.id
        instance1.odoo_id = _odoo_version.id
        self.assertEqual(_odoo_version.instance_nums, 2)
        
        
