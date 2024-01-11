from odoo import exceptions, fields
from odoo.tests import common
from datetime import datetime, timedelta

class TestKzmInstanceRequest(common.SingleTransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestKzmInstanceRequest, self).setUp(*args, **kwargs)
        admin_user = self.env.ref('base.user_admin')
        self.kzm_instance_request = self.env['kzm.instance.request'].with_user(
            admin_user)
        self.kzm_instance = self.kzm_instance_request.create({
            'cpu': 'Intel Core I7',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Soumise',
        })

    def test_change_to_Brouillon(self):
        """it should be Changed to Brouillon method"""
        self.kzm_instance.change_to_Brouillon()
        self.assertEqual(self.kzm_instance.state, "Brouillon")

    def test_change_to_Soumise(self):
        """it should be Changed to Soumise method"""
        self.kzm_instance.change_to_Soumise()
        self.assertEqual(self.kzm_instance.state, "Soumise")

    def test_change_to_En_Traitement(self):
        """it should be changed to En traitement method"""
        self.kzm_instance.change_to_En_Traitement()
        self.assertEqual(self.kzm_instance.state, "En traitement")

    def test_change_to_Traitee(self):
        """it should be changed to Traitee"""
        self.kzm_instance.change_to_Traitee()
        self.assertEqual(self.kzm_instance.state, "Traitee")

    def test_unlink(self):
        """the instance to delete"""
        self.kzm_instance = self.kzm_instance_request.create({
            'cpu': 'Intel Core I7',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Soumise',
        })
        with self.assertRaises(exceptions.UserError):
            self.kzm_instance.unlink()

    def test_check_and_change(self):
        """Test the check and change"""
        self.kzm_instance = self.kzm_instance_request.create({
            'cpu': 'Intel Core I7',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Traitee',
        })
        now_date = fields.Date.today()
        self.kzm_instance.limit_date = datetime(now_date.year, now_date.month, now_date.day + 2)
        self.kzm_instance.check_state_and_change()
        self.assertEqual(self.kzm_instance.state, "Soumise")
    
    
    def test_compute_treat_duration(self):
        """Test compute treat duration"""
        self.kzm_instance = self.kzm_instance_request.create({
            'cpu': 'Intel Core I7',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Traitee',
        })
        self.kzm_instance.treat_date = datetime.now() + timedelta(days=5)
        self.assertEqual(self.kzm_instance.treat_duration, 4.0)
        
    def test_compute_perimeter_nums(self):
        """Test compute perimeter nums"""
        perimeter0 = self.env['perimeter.perimeter'].create({
            'name': 'Sales'
        })
        perimeter1 = self.env['perimeter.perimeter'].create({
            'name': 'Documents'
        })
        perimeter2 = self.env['perimeter.perimeter'].create({
            'name': 'Agriculture'
        })
        perimeter3 = self.env['perimeter.perimeter'].create({
            'name': 'Projects'
        })
        kzm_instance = self.kzm_instance_request.create({
            'cpu': 'Intel Core I7',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Traitee',
        })
        kzm_instance.perimeters_ids = [perimeter0.id]
        self.assertEqual(kzm_instance.perimeters_nums, 1)
        # kzm_instance.perimeters_ids.append(perimeter1.id)
        # kzm_instance.perimeters_ids.append(perimeter2.id)
        # kzm_instance.perimeters_ids.append(perimeter3.id)
        # self.assertEqual(kzm_instance.perimeters_nums,4)

    def test_create(self):
        """Test create Record"""
        kzm_instance = self.kzm_instance_request.create({
            'cpu': 'Intel Core I7',
            'ram': '256GB',
            'disk': '1 TB',
            'url': 'www.mmoumni.me',
            'state': 'Traitee',
        })
        self.assertEqual(kzm_instance.cpu, 'Intel Core I7')
        self.assertEqual(kzm_instance.ram, '256GB')
        self.assertEqual(kzm_instance.disk, '1 TB')
        self.assertEqual(kzm_instance.url, 'www.mmoumni.me')
        self.assertEqual(kzm_instance.state, 'Traitee')
    
    
    # def test_write(self):
    #     """Test write"""
        
