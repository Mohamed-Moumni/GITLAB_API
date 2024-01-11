# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "kZM Base Setup",
    'version': '16.0.1.0.1',
    "author": "Karizma",
    "license": 'AGPL-3',
    "summary": "Install base setup",
    "website": "http://www.karizma.ma",
    "category": 'Tools',
    "sequence": 20,
    "depends": ['base'],
    "data": [
        "data/install_base_setup_function.xml",
    ],
    "installable": True,
    'auto_install': True,
    "application": False,
}
