# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "kZM Image Importation",
    "version": "16.0.1.0.1",
    "author": "Karizma",
    "license": 'LGPL-3',
    "summary": "",
    "website": "http://www.karizma.ma",
    "category": 'Tools',
    "sequence": 20,
    "depends": [
        'base',
        'base_setup',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/import_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {"python": ["pydrive"]},
}
