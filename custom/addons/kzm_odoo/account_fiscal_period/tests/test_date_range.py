# -*- coding: utf-8 -*-


import datetime
from odoo.addons.date_range.tests.test_date_range import DateRangeTest


class DateRangeTestInherit(DateRangeTest):
    def setUp(self):
        super(DateRangeTestInherit, self).setUp()

    def test_default_company(self):
        super(DateRangeTestInherit, self).test_default_company()

    def tes_is_fiscal_period(self):
        print(self.type.fiscal_period)

    def test_domain(self):
        dr = self.date_range.create(
            {
                "name": "FS2015",
                "date_start": "2020-01-01",
                "date_end": "2020-12-31",
                "type_id": self.type.id,
            }
        )
        domain = dr.get_domain("my_field")
        # By default the domain include limits
        self.assertEqual(
            domain,
            [
                ("my_field", ">=", datetime.date(2015, 1, 1)),
                ("my_field", "<=", datetime.date(2015, 12, 31)),
            ],
        )
