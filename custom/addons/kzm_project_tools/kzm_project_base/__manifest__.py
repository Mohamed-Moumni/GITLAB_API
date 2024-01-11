# -*- coding: utf-8 -*-
{
    'name': "kzm_project_base",

    'summary': """
        ce module gère les différents aspects liés au contrat cadre du Karizma consulting group""",

    'description': """
        ce module gère les différents aspects liés au contrat cadre du Karizma consulting group
    """,

    'author': "Karizma Consulting group, Otman El agy",
    'website': "https://karizma-conseil.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'project', 'analytic', 'sale_subscription',
                'helpdesk_timesheet', 'crm',
                'kzm_backup_tracker', 'sale_crm', 'helpdesk', 'portal', 'mail'],

    # always loaded
    'data': [
        'data/activities.xml',
        'data/sequence.xml',
        'data/fetch_cron.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_config_setting.xml',
        'views/contract_cadre.xml',
        'views/project_carnet.xml',
        'views/project_task.xml',
        'views/product_template.xml',
        # 'views/sale_subscription.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/crm_lead.xml',
        'views/helpdedsk_ticket.xml',
        'views/account_analytic_line.xml',
        'views/module_branche.xml',
        'views/project_module.xml',
        'views/module_tag.xml',
        'views/ressource_type.xml',
        'views/service_type.xml',
        'views/odoo_version.xml',
        'views/project_database.xml',
        'views/project_ressource.xml',
        'views/res_partner.xml',
        'views/kzm_backup_tracker.xml',
        'views/affectation_ressource.xml',
        'views/dashboard.xml',
        'views/openticket_form.xml',
        'views/helpdesk_views.xml',
        'views/myinvoices.xml',
        'views/myorders.xml',
        'views/timesheet_portal.xml',
        'views/tasks_portal.xml',
        'views/subscriptions_portal.xml',
        'views/carnets_portal.xml',
        # 'views/task_request.xml',
        'views/derogation_Sold_task.xml',
        'views/logger_failed_mails.xml',
        'wizard/affectation_ticket_views.xml',
        'wizard/derogation_validation.xml',
        'demo/demo.xml',
        'views/helpdesk_ticket_views.xml',
    ],
    # only loaded in demonstration mode
}
