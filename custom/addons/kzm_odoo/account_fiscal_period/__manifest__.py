# -*- coding: utf-8 -*-

{
    'name': 'Account Fiscal Period',
    'version': '16.0.0',
    'category': 'Accounting',
    'author': 'Andeùa',
    "license": 'LGPL-3',
    'website': 'http://www.andemaconsulting.com',
    'depends': [
        'date_range',
    ],
    'data': [
        'security/date_range_security.xml',
        'security/ir.model.access.csv',
        'data/date_range_type.xml',
        # 'views/date_range_type.xml',
        'views/date_range.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
