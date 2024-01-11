# -*- coding: utf-8 -*-
{
    'name': "KZM FTP",
    'summary': """""",
    'description': """
        This module allows you to test FTP Connexion
    """,
    'author': "AHMED MAJID | Karizma Consulting Group",
    'website': "https://karizma-conseil.com",

    # Categories can be used to filter modules in modules listing

    'category': 'Tools',
    'version': '16.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ftp_connexion_test_views.xml',
    ],
}
