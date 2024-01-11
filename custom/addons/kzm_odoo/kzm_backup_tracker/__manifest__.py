# -*- coding: utf-8 -*-
{
    'name': "GCloud Backup Tracker",

    'summary': """
        This module is about establish a connection to an GCloud bucket with Odoo
        ERP""",

    'author': "Karizma",
    'website': "https://karizma-conseil.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data
    # /ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '16.0.1.0.1',
    "license": 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'planning'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/mail_template_data.xml',
        'views/db_backup.xml',
        'views/gantt.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
