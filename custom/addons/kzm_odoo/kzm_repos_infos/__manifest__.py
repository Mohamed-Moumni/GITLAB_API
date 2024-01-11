# -*- coding: utf-8 -*-
{
    'name': "Repos modules infos",
    'summary': """Returns the infos of modules in an organizations repositories""",
    'description': """""",
    'author': "Karizma Conseil, Assabe POLO",
    'website': "",
    'category': 'Tools',
    'version': '16.0.0',
    # any modue necessary for this one to work correctly
    'depends': ['kzm_base', 'queue_job'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    "external_dependencies": {"python": ["github"]},
    'license': 'LGPL-3',
}
