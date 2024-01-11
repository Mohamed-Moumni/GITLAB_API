# -*- coding: utf-8 -*-
{
    'name': "KZM DISABLE",

    'summary': """
       KZM DISABLE
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Karizma Conseil, ZAKARIA",
    'website': "https://karizma-group.com/",


    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',

    ],
    'installable': True,
    "auto_install": True,
}
