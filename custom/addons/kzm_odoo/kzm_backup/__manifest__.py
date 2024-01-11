# -*- coding: utf-8 -*-
{
    'name': "kzm_backup",

    'summary': """Manage Odoo Instance backup""",
    'author': "KARIZMA CONSEIL",
    'website': "http://www.karizma.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module
    # /module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'mail',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/instance_views.xml',
        'views/backup_views.xml',
        'data/mail.xml',

    ],
    "external_dependencies": {"python": ["fabric"]},
    # only loaded in demonstration mode
    'demo': [

    ],
}
