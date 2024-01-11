# -*- coding: utf-8 -*-
{
    'name': "KZM KEY SERVER",

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
    'depends': ['base', 'kzm_project_base', 'kzm_db_res_users'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/synch_data_wizard.xml',
        'views/project_database_views.xml',
        'views/database_metadata_views.xml'

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
