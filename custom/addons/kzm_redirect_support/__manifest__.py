{
    'name': "KZM Redirect Support",
    'summary': "Karizma Redirect Support",
    'description': """A module that add the karizma support in the menu item""",
    'author': "Mohamed Moumni",
    'license': "AGPL-3",
    'category': 'Uncategorized',
    'version': '16.0',
    'depends': ['base_setup',
                'mail',
                'web',
                'web_enterprise',
                'web_editor',],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'kzm_redirect_support/static/src/js/user_menuitems.js',
        ],
    },
    'demo': [],
    'application': True,
    # 'auto_install': True,
    # 'installable': True
}
