{
    'name': "kzm_gitlab_monitoring",
    'summary': "Karizma Gitlab Monitoring",
    'author': "Mohamed Moumni",
    'license': "AGPL-3",
    'category': 'Uncategorized',
    'version': '16.0',
    'depends': ['base', 'kzm_project_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/gitlab_credential_view.xml',
        'views/project_instance_view.xml',
    ],
    'assets': {
        'web.assets_common': [
            'kzm_gitlab_monitoring/static/src/css/kanban.css',
            ],
    },
    'demo': [],
    'application': True,
    'auto_install': True,
    'installable': True
}
