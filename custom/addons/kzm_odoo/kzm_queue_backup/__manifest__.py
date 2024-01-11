# -*- coding: utf-8 -*-
{
    'name': "Queue backup management",
    'summary': """Permets de gérer les backup avec des jobs.""",
    'description': """ """,
    'author': "K.joel, Karizma conseil",
    'website': "http://www.karizma-conseil.com",
    'category': 'Tools',
    'version': '16.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'oca_auto_backup_extension', 'queue_job'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/backup_cron.xml',
        'views/db_backup_views.xml',
    ],

}
