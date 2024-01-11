# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "KZM Support",
    "version": "0.2.3",
    "author": "Karizma",
    "license": 'AGPL-3',
    "description": """
    """,
    "summary": "",
    "website": "http://www.karizma.ma",
    "category": 'Tools',
    "sequence": 20,
    "depends": [
        'website_helpdesk_form',
        'helpdesk_timesheet',
    ],
    "data": [
        "data/data_helpdesk_ticket_type.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/helpdesk_views.xml",
        "views/helpdesk_templates.xml",
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
