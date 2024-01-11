# -*- coding: utf-8 -*-
{
    'name': "kzm_helpdesk",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Karizma Conseil & Integration",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'sale_subscription', 'project', 'helpdesk_timesheet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sla_subscription_view.xml',
        'views/helpdesk_ticket_view.xml',
        'views/product_product_view.xml',
        'views/sale_subscription_views.xml',
        'views/res_company_views.xml',
        'views/sale_subscription_service_views.xml',
        'views/sale_subscription_odoo_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
