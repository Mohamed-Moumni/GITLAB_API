# -*- coding: utf-8 -*-
{
    'name': "kzm_helpdesk_portal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        User Portal Interface
    """,

    'author': "Karizma Conseil & Integration",
    'website': "https://karizma-conseil.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_helpdesk_form'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        "data/data_helpdesk.xml",
        'views/helpdesk_template.xml',
        'views/helpdesk_views.xml',
        'views/subscription_template.xml',
    ],
    # only loaded in demonstration mode

}