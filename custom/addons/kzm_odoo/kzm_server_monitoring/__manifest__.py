# -*- coding: utf-8 -*-
{
    'name': "kzm_server_monitoring",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '16.0.1.0.1',
    'depends': ['base', 'mail', 'kzm_backup_tracker'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/server_config.xml',
        'views/instance_monitoring.xml',
        'views/server_config_admin.xml',
        'views/menu.xml',
        'data/cron_instances_create.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
