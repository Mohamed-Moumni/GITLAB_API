# -*- coding: utf-8 -*-

import datetime

from odoo import fields, models, _, api
from odoo.exceptions import UserError


class DerogationValidation(models.TransientModel):
    _name = 'derogation.validation'
    _description = 'derogation validation'

    name = fields.Char(string=_('Task name'), required=True)
    partner_id = fields.Many2one('res.partner', string=_("Client"), required=True)
    project_id = fields.Many2one('project.project', string=_('Project'),
                                 required=True)
    domain_partner = fields.Many2many('res.partner', string="Client domain")
    derogation_id = fields.Many2one('sold.task.derogation', string=_("Derogation"))

    domain_project = fields.Many2many('project.project', string="project domain")

    @api.depends('partner_id')
    def _compute_project_id(self):
        for rec in self:
            domain = []
            if rec.partner_id:
                domain = ['|', ('contract_id', '=', False), ('partner_id', '=', rec.partner_id.id)]
            print("domain", domain)
            projects = self.env['project.project'].search(domain)
            if projects:
                rec.domain_project = projects.ids
            else:
                rec.domain_project = False

    def validate(self):
        if self.project_id:
            stage = self.env['project.task.type'].search([('sequence', '=', 1)], limit=1)
            task = self.env['project.task'].create({
                'name': self.name,
                'project_id': self.project_id.id,
                'partner_id': self.partner_id.id,
                'contract_id': self.derogation_id.contract_id.id,
                'stage_id': stage.id,
                'planned_hours': self.derogation_id.estimated_time,
            })
            print("----", task)
            if task:
                self.derogation_id.created_task_id = task.id
                self.derogation_id.state = 'validated'

    # @api.depends('partner_id')
    # def _get_domain_project(self):
    #     domain = []
    #     if self.partner_id:
    #         domain = ['|', ('contract_id', '=', False), ('partner_id', '=', self.partner_id.id)]
    #     print("domain", domain)
    #     projects = self.env['project.project'].search(domain)
    #     if projects:
    #         r.domain_project = projects.ids
    #     else:
    #         r.domain_project = False
