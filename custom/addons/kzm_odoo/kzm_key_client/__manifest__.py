# -*- coding: utf-8 -*-
{
    'name': "Kzm Key Client",

    'summary': """KZM Key Client""",

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
    'depends': ['base', 'kzm_db_res_users', 'hr', 'kzm_base'],

    # always loaded
    'data': [
        # 'data/res_users_data.xml',
        'security/security.xml',
        'views/res_users_views.xml'

    ],

    # only loaded in demonstration mode
    'demo': [

    ],
    "auto_install": True,
    "installable": True,
}
