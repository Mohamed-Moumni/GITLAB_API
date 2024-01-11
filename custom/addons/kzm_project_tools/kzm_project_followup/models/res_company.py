# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    hrs_per_day = fields.Float("Works hours/day", help="Number of work hours per day", default=8.0)
