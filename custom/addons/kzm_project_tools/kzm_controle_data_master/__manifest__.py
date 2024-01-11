# -*- coding: utf-8 -*-
{
    'name': "Kzm Controle Data Master",

    'summary': """
    Controle Data
    """,

    'description': """
        Controle Data Ping
    """,

    'author': "Karizma Conseil, ZAKARIA ELGHANDORI",
    'website': "https://karizma-group.com/",

    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kzm_key_server', 'web'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/controle_data_master.xml',
    ],
}
