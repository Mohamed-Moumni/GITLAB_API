# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Karizma Project Global Evaluation ',
    'version' : '11.0',
    'summary': 'Project Evaluation, Equipes, PEvaluation...',
    'description': """
        Project Evaluation  2
    """,
    'category': 'HR',
    'author': "Abdelmajid ELhamdaoui, KARIZMA CONSEIL",
    'website': 'http://www.karizma-conseil.com',
    'images': [
    ],
    'depends': [
        'kzm_hr_evaluation',
        'kzm_project_followup',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/prj_eval_views.xml',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    #'post_init_hook': '_auto_install_l10n',
}
