# -*- coding: utf-8 -*-
{
    'name': "KZM ACCESS RIGHTS",
    'summary': """The purpose of this module is to prevent a user with access rights from being able to switch to settings rule""",
    'description': """
       The purpose of this module is to prevent a user with access rights from being able to switch to settings rule
    """,
    'author': "Ahmed MAJID | Karizma Consulting Group",
    'website': "https://karizma-conseil.com",

    # Categories can be used to filter modules in modules listing

    'category': 'Tools',
    'version': '16.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

    ],
}
