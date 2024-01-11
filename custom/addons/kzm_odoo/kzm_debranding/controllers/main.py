# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json

from ast import literal_eval
from copy import deepcopy
from lxml import etree

import odoo
from odoo import http, _
from odoo.http import content_disposition, request
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import ustr, sql


class CustomController(http.Controller):

    @http.route('/web_studio/set_background_image', type='json', auth='user')
    def set_background_image(self, attachment_id):
        attachment = request.env['ir.attachment'].browse(attachment_id)
        if attachment:
            request.env.company.background_image = attachment.datas

