{
    'name': 'GPT Chatbot',
    'version': '1.0',
    'category': 'ExtraTools',
    'summary': 'Integrate GPT Chatbot with Odoo',
    'author': 'Your Name',
    'website': 'https://www.example.com',

    'license': 'AGPL-3',
    'depends': ['base', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/chatgpt_request_views.xml',
        'views/chatgpt_request_line_views.xml',
        'views/chatgpt_pricing_views.xml',
        'views/chatgpt_model_views.xml',
        'views/chatgpt_training_data_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
