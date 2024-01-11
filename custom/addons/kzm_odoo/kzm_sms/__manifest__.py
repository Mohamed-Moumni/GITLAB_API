# -*- coding: utf-8 -*-
{
    'name': "KZM SmS",
    'summary': """Long description of module's purpose""",
    'author': "Karizma Group",
    'website': "https://karizma-conseil.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data
    # /ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '16.0.1.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
