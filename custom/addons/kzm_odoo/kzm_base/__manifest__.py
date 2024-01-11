# encoding: utf-8
##############################################################################
#
#    Localisation marocaine module for OpenERP, Localisation marocaine, Les bases
#    Copyright (C) 2014 (<http://www.example.org>) Anonym
#
#    This file is a part of Localisation marocaine
#
#    Localisation marocaine is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Localisation marocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Module Karizma: Base Localisation Marocaine',
    'version': '16.0.1.0.1',
    'author': 'KARIZMA CONSEIL',
    'category': 'Localisation marocaine',
    'summary': """
        Pour gérer : Paie, Liasse fiscale, TVA, Immobilisation
        Localisation marocaine - La base
        ================================
    """,
    'website': 'http://www.karizma.ma',
    'images': [],
    'depends': ['base', 'web', 'base_setup'],
    "license": "AGPL-3",
    'data': [
        # 'security/groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/menus.xml',
        'data/precision.xml',
        'data/bank.xml',
        'data/commune.xml',
        'data/forme_juridique.xml',
        'views/templates.xml',
        'views/company.xml',
        'views/commune.xml',
        'views/partner_view.xml',
        'views/ir_qweb.xml',
        'views/base_config_view.xml'

    ],
    'installable': True,
    'auto_install': True,
    'application': True,

    'test': [
        'tests/users.yml',
        'tests/sequence.yml',
    ],
}
