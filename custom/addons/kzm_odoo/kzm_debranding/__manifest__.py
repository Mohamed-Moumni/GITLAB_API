# -*- coding: utf-8 -*-
{
    'name': "KZM DEBRANDING",

    'summary': """
        KZM DEBRANDING""",

    'author': "Karizma GROUP, MAJID Ahmed",
    'website': "https://karizma-group.com/",

    'category': 'Uncategorized',
    'version': '16.0',
    'application': False,

    # any module necessary for this one to work correctly
    'depends': ['base_setup',
                'mail',
                'web',
                'web_enterprise',
                'web_editor',
                # 'payment'
                ],

    # always loaded
    'data': [
        # 'views/assets.xml',
        'views/res_config_settings_view.xml',
        # 'views/payment_views.xml'
    ],
    'assets': {

        'web.assets_common': [
            'kzm_debranding/static/src/scss/ui_login.scss',
        ],
        'web.assets_frontend': [
            'kzm_debranding/static/src/scss/ui_login.scss',
        ],
        'web.assets_backend': [
            # 'kzm_debranding/static/src/js/background_image.js',
            'kzm_debranding/static/src/xml/home_background.xml',
            'kzm_debranding/static/src/xml/res_config_edition.xml',
            'kzm_debranding/static/src/js/user_menuitems.js',
            'kzm_debranding/static/src/js/home_menu.js',
            'kzm_debranding/static/src/js/menus.js',
            'kzm_debranding/static/src/css/customize_css.css',
            'kzm_debranding/static/src/scss/ui.scss',
            # 'kzm_debranding/static/src/scss/ui_login.scss',

        ],

        'web.assets_qweb': [

        ],
    },
    # 'qweb': [
    #     'kzm_debranding/static/src/xml/*.xml',
    # ],
    # only loaded in demonstration mode
}
