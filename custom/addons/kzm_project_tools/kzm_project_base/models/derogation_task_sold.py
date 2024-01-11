# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SoldTaskDerogation(models.Model):
    _name = 'sold.task.derogation'
    _inherit = 'mail.thread'
    _description = 'Sold task Derogation'

    name = fields.Char(string=_("Name"), readonly=True)
    user_id = fields.Many2one('res.users', string=_('Asked by'), default=lambda self: self.env.user, readonly=True)
    date = fields.Date(string=_('Date'), default=fields.Date.today())
    # partner_id = fields.Many2one('res.partner', string=_('Client'), domain=[('customer_rank', '>', 0)], tracking=True,
    #                              required=1)

    task_id = fields.Many2one('project.task', string=_('Task'), tracking=True)
    created_task_id = fields.Many2one('project.task', string=_('Created task'), tracking=True)
    # project_id = fields.Many2one('project.project', string=_('Project'), related="task_id.project_id")
    initial_sold = fields.Float(string=_("Initial sold"), tracking=True, related="task_id.planned_hours")
    sold = fields.Float(string=_("Actual Sold"), tracking=True, related="task_id.sold")

    contract_id = fields.Many2one('contract.cadre', string=_('Contract cadre'),
                                  store=True, tracking=True, required=1)
    pattern = fields.Text(string=_("Pattern"), tracking=True, required=1)
    domain_project = fields.Many2many('project.project', string="project domain", compute="_compute_contract_id")
    domain_partner = fields.Many2many('res.partner', string="Client domain", compute="_compute_contract_id")
    estimated_time = fields.Float(string=_("Estimated charge"), tracking=True, required=1)
    state = fields.Selection([
        ("draft", "Draft"),
        ("on_hold", "In wait"),
        ("validated", "Validated"),
        ("refused", "Refused")],
        string=_("State"),
        default="draft", tracking=True)
    type = fields.Selection([
        ("new_task", "New task"),
        ("Sold_increase", "Balance increase")], string=_("Type of request"),
        default="new_task", tracking=True, required=1)
    name_ticket = fields.Char(string=_('Task name'))

    @api.depends('contract_id', 'contract_id.customer_id', 'contract_id.secondary_customer_ids')
    def _compute_contract_id(self):
        for rec in self:
            # contract = False
            # if rec.partner_id:
            #     contract = rec.env['contract.cadre'].sudo().search(
            #         ['|', ('customer_id', '=', rec.partner_id.id), '|',
            #          ('secondary_customer_ids', 'in', rec.partner_id.id),
            #          ('contact_ids', 'in', rec.partner_id.id),
            #          ], order='first_date DESC', limit=1
            #     )
            # rec.contract_id = contract
            domain = []
            if rec.contract_id:
                domain = ['|', ('collective_project', '=', True), ('contract_id', '=', rec.contract_id.id)]
            print("domain", domain)
            projects = self.env['project.project'].search(domain)
            if projects:
                rec.domain_project = projects.ids
            else:
                rec.domain_project = False
            domain1 = self.env['res.partner']
            if rec.contract_id:
                if rec.contract_id.customer_id:
                    domain1 += rec.contract_id.customer_id
                if rec.contract_id.secondary_customer_ids:
                    domain1 += rec.contract_id.secondary_customer_ids
            if domain1:
                rec.domain_partner = domain1.ids

    @api.model
    def create(self, vals):
        if vals['type'] == 'new_task':
            seq = "TR%s" % (self.env['ir.sequence'].next_by_code('sold.task.derogation')) or 'New'
        else:
            seq = "DTS%s" % (self.env['ir.sequence'].next_by_code('sold.task.derogation')) or 'New'
        vals['name'] = seq
        return super(SoldTaskDerogation, self).create(vals)

    def set_to_on_hold(self):
        if self.state == 'draft':
            self.state = 'on_hold'

    def set_to_validate(self):
        if self.state == 'on_hold' and self.type == 'new_task':
            action = self.env['ir.actions.act_window']._for_xml_id('kzm_project_base.derogation_validation_view_action')
            if self.contract_id.project_ids:
                project = self.contract_id.project_ids[0].id
            else:
                project = False
            action['context'] = {'default_derogation_id': self.id,
                                 'default_name': self.name_ticket,
                                 'default_partner_id': self.contract_id.customer_id.id,
                                 'default_project_id': project,
                                 'default_domain_project': self.domain_project.ids,
                                 'default_domain_partner': self.domain_partner.ids}
            return action
        elif self.state == 'on_hold':
            self.task_id.planned_hours += self.estimated_time
            self.state = 'validated'

    def set_to_refuse(self):
        if self.state == 'on_hold':
            self.state = 'refused'

    def set_to_draft(self):
        if self.state in ['validated', 'refused']:
            self.state = 'draft'

    @api.onchange('contract_id')
    def task_domain(self):
        for r in self:
            r.task_id = False


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_progress = fields.Boolean("Is in progress", default=False)
