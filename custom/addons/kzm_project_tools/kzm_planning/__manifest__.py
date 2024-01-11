# -*- coding: utf-8 -*-
{
    'name': "kzm_planning",

    'summary': """ KZM Plannig """,

    'author': "Karizma-conseil",
    'website': "http://www.karizma-conseil.com",
    "license": "AGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kzm_project_base', 'project', 'helpdesk', 'planning', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data_sequence.xml',
        'data/ir_cron.xml',
        'data/mail_template.xml',
        'views/menu.xml',
        'views/planification_planification.xml',
        'views/planification_line.xml',
        'views/planning_slot.xml',
        'views/project_task.xml',
        'views/planification_activity_line.xml',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/task_consumption.xml',
        'views/task_consumption_line.xml',
        'views/sold_ticket_derogation.xml',
        'reports/task_consumption_reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'kzm_planning/static/src/xml/gantt_view.xml',
            'kzm_planning/static/src/xml/calendar_view.xml',
            'kzm_planning/static/src/js/planning_gantt_row.js',
        ],
    },

}
