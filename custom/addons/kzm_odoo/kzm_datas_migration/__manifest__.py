# -*- coding: utf-8 -*-
{
    'name': "KZM DATA MIGRATION",

    'summary': """KZM DATA MIGRATION""",

    'description': """
    """,

    'author': "KARIZMA CONSEIL",
    'website': "http://www.karizma.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module

    # for the full list
    'category': 'Tools',
    'version': '16.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kzm_datas_migration_views.xml',
        'views/account_journal_views.xml',
        'views/account_tax_views.xml',
        'views/res_partner_views.xml',
        'views/account_account_views.xml',
        'views/account_move_views.xml',

    ],

    # only loaded in demonstration mode
    'demo': [

    ],
}
