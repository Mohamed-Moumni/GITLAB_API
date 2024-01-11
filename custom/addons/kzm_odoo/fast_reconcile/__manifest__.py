# -*- coding: utf-8 -*-
{
    'name': "fast_reconcile",

    'summary': "Module for fast reconciliation",

    'description': """
        Long description of module's purpose
    """,

    'author': "Dounia Bennoune, karizma conseil",
    'website': "https://karizma-conseil.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_mass_reconcile'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_fast_reconcile.xml',
        'views/account_fast_reconcile_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
