# -*- coding: utf-8 -*-
{
    'name': "Kzm DB Res Users",

    'summary': """KZM DB RES USERS""",

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
    'depends': ['base'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv'

    ],

    # only loaded in demonstration mode
    'demo': [

    ],
}
