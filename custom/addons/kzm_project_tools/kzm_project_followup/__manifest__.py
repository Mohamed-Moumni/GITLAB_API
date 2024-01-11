# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Karizma Project Evaluation',
    'version': '11.0',
    'summary': 'Project Evaluation, Lot, Phase, charges...',
    'description': """
        Project Evaluation 
    """,
    'category': 'HR',
    'author': "Abdelmajid ELhamdaoui, KARIZMA CONSEIL",
    'website': 'http://www.karizma-conseil.com',
    'images': [
    ],
    'depends': [
        'kzm_hr_evaluation',
        'project',
        'sale',
        'hr_timesheet',
        'account',
        'project_task_code',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/eval_views.xml',
        'views/res_company.xml',
        'views/project_task_views.xml',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    # 'post_init_hook': '_auto_install_l10n',
}
