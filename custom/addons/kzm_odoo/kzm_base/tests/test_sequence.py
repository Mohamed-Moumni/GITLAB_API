# -*- coding: utf-8 -*-

import time
from openerp.tests.common import TransactionCase


class Sequence(TransactionCase):

    def setUp(self):
        super(Sequence, self).setUp()
        self.sequence_model = self.registry('ir.sequence')

    def test_seq(self):
        crm, uid = self.cr, self.uid
        seq_id = self.sequence_model.create(crm, uid, {
            'name': 'year2',
            'prefix': 'F%(year2)s',
        })
        val = 'F' + time.strftime('%Y')[2:4]
        result = self.sequence_model._next(crm, uid, [seq_id])
        result = result[:3]
        self.assertEqual(val, result, f"The result [{result}] should be [{val}]")
