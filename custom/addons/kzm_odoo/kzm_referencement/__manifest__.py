# -*- coding: utf-8 -*-
{
    'name': "KZM REFERENCEMENT",
    'summary': """
        KZM REFERENCEMENT """,
    'author': "Karizma Conseil et Integration",
    'website': "http://www.karizma.ma",
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '16.0.1.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'purchase'],
    # always loaded
    'data': [
        'security/security.xml',
        #'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
    ],

}
