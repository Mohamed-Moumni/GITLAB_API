# -*- coding: utf-8 -*-
{
    'name': "KZM BULK SMS API",

    'summary': """
      sending SMS using Bulk SMS API""",

    'description': """
    """,

    'author': "Karizma Consulting Group",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sms', 'mass_mailing_sms'],

    # always loaded
    'data': [
        'views/res_config.xml',
    ],
}
