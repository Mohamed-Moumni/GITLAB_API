# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Karizma HR Evaluation',
    'version' : '11.0',
    'summary': 'HR Evaluation, Axe, Note, Plan...',
    'description': """
        Hr Evaluation 
    """,
    'category': 'HR',
    'author': "Abdelmajid ELhamdaoui, KARIZMA CONSEIL",
    'website': 'http://www.karizma-conseil.com',
    'images': [
    ],
    'depends': [
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/eval_views.xml',
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
