# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    project_subscription_id = fields.Many2one('project.project', string="Project Subscription")