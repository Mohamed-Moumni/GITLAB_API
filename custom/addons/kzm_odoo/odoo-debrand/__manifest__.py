# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Tintuk Tomin(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': "Odoo Debranding",
    'version': "16.0.1.2.2",
    'summary': """Odoo Backend and Front end Debranding""",
    'description': """Debrand Odoo,Debranding, odoo13""",
    'author': "Cybrosys Techno Solutions",
    'company': "Cybrosys Techno Solutions",
    'maintainer': "Cybrosys Techno Solutions",
    'website': "https://cybrosys.com/",
    'category': 'Tools',
    'depends': ['website', 'base_setup'],
    'data': [
        'views/views.xml',
        'views/res_config_views.xml',
        'views/ir_module_views.xml'
    ],
    'qweb': ["static/src/xml/base.xml"],
    'images': ['static/description/banner.gif'],
    'license': "AGPL-3",
    'installable': True,
    'application': False,
    'web.assets_backend': [
        'survey/static/src/question_page/*',
        'odoo-debrand/static/src/js/title.js'
    ],
}
