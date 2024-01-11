# -*- coding: utf-8 -*-


from openerp.tests.common import TransactionCase
from openerp.addons.kzm_base.controllers.tools import date_range as dr


class DateRange(TransactionCase):

    def setUp(self):
        super(DateRange, self).setUp()

    def test_with_datetime(self):
        from openerp.addons.kzm_base.controllers.tools import date_range as dr
        from datetime import datetime
        day = datetime(year=2015, month=8, day=16)
        dt_from, dt_to = dr(day)
        self.assertEqual(dt_from, '2015-08-01', "The result should be 2015-08-01")
        self.assertEqual(dt_to, '2015-08-31', "The result should be 2015-08-31")

    def test_with_string(self):
        day = '2015-08-16'
        dt_from, dt_to = dr(day)
        self.assertEqual(dt_from, '2015-08-01', "The result should be 2015-08-01")
        self.assertEqual(dt_to, '2015-08-31', "The result should be 2015-08-31")
