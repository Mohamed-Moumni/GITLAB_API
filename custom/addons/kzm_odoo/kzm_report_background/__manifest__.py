# -*- coding: utf-8 -*-
{
    'name': "kzm report background",

    'summary': """
        Ce module permet d'ajouter des arrière-plans aux rapports en supprimant l'en-tête et la fin de page""",

    'author': "Karizma conseil",
    'website': "https://karizma-conseil.com",
    'license': "AGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1.0.1',

    # any module nec,essary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/paperformat_euro.xml',
        'reports/external_layout_boxed.xml',
        # 'data/report_layout.xml',
        'views/res_config.xml',
    ],
}
