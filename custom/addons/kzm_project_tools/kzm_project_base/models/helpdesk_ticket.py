# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def _get_default_custom_tag_ids(self):
        task_id = self.env.context.get('default_task_id', False)
        task_id = self.env['project.task'].browse(task_id)
        return task_id.custom_tag_ids if task_id else False

    internal_type = fields.Selection([
        ("Abonnement", "Abonnement"),
        ("carnet", "Carnet"),
        ("project", "Projet")],
        string=_("Nature"))
    # parent_partner_id = fields.Many2one('res.partner', related="partner_id.parent_id")
    domain_project = fields.Many2many('project.project', compute="_get_domain", string="project domain", store=True)
    project_id = fields.Many2one('project.project', related="task_id.project_id", string=_("Project"), readonly=0)
    domain_task = fields.Many2many('project.task', compute="_get_domain", string="tasks domain")
    task_id = fields.Many2one('project.task', string=_("Task"), domain="[('id','in',domain_task)]", store=True)
    contract_id = fields.Many2one('contract.cadre', compute="_compute_contract_id", store=True, string="Contract cadre")
    sold = fields.Float(string="Solde", compute="_compute_task_sold")
    last_message = fields.Many2one('res.partner', compute='_compute_last_message', string="Dernier message")
    estimated_charge = fields.Float(string="Charge estimée", tracking=True, store=1)
    real_charge = fields.Float(string="Charge réelle", compute="_compute_real_charge")
    ancien_consommation = fields.Float(string="Ancienne consommation")
    planned_date = fields.Date(string="Date de planification")
    feedback_date = fields.Date(string="feedback Date")
    old_carnet = fields.Char(string="Ancien carnet")
    write_task = fields.Boolean('Ouvrir Tâche')
    is_timesheet = fields.Boolean(compute="compute_is_timesheet")

    partner_email = fields.Char(inverse="")

    real_charge_portal = fields.Float(string="Charge réelle (Portail)")
    custom_tag_ids = fields.Many2many('custom.project.tags', 'ticket_custom_tags_rel', string="Consignes",
                                      default=_get_default_custom_tag_ids)

    @api.onchange('task_id')
    def _onchange_task_id_2(self):
        for record in self:
            record.custom_tag_ids = record.task_id.custom_tag_ids

    @api.onchange('timesheet_ids', 'timesheet_ids.unit_amount')
    def _onchange_real_charge_portal(self):
        for record in self:
            record.real_charge_portal = sum(record.timesheet_ids.mapped('unit_amount'))

    def _inverse_real_charge_portal(self):
        """inverse"""
        pass

    @api.constrains('stage_id')
    def _check_stage_id(self):
        for record in self:
            if record.stage_id.is_clotured and not record.real_charge:
                msg = "Unable to close a ticket with 0 hours spent"
                raise ValidationError(msg)

    @api.depends('timesheet_ids')
    def compute_is_timesheet(self):
        for rec in self:
            rec.is_timesheet = False
            if rec.timesheet_ids:
                rec.is_timesheet = True

    @api.onchange('partner_id')
    def reset_partner_id(self):
        for record in self:
            if record.partner_id and record.create_date:
                record.task_id = False

    @api.depends('task_id', 'task_id.sold')
    def _compute_task_sold(self):
        for rec in self:
            rec.sold = 0
            if rec.task_id:
                rec.sold = rec.task_id.sold

    @api.depends('timesheet_ids', 'timesheet_ids.unit_amount')
    def _compute_real_charge(self):
        for rec in self:
            rec.real_charge = 0
            timesh = self.env['account.analytic.line'].sudo().search([('helpdesk_ticket_id', '=', rec._origin.id)])
            if rec.create_date:
                rec.real_charge = sum([l.unit_amount for l in timesh])

    def _compute_last_message(self):
        for rec in self:
            last_messages_ticket = rec.env['mail.message'].search(
                [('res_id', "=", rec.id), ('model', "=", "helpdesk.ticket")], order='create_date DESC', limit=1)
            if last_messages_ticket:
                rec.last_message = last_messages_ticket.author_id
            else:
                rec.last_message = False

    # @api.model
    # def create(self, vals):
    #     try:
    #         return super(HelpdeskTicket, self).create(vals)
    #     except Exception as e:
    #         _logger.info(
    #             'fetched mail failed to create a ticket')
    #         # if isinstance(message, xmlrpclib.Binary):
    #         #     message = bytes(message.data)
    #         # if isinstance(message, str):
    #         #     message = message.encode('utf-8')
    #         # message = email.message_from_bytes(message, policy=email.policy.SMTP)
    #         #
    #         # msg_dict = MailThread.message_parse(message, save_original=False)
    #         self.env['logger.failed.mail'].create(
    #             {'name': 'test', 'message_id': 'test1',
    #              'client_mail': 'test2', 'date': 'test3'})

    @api.onchange('stage_id')
    def set_closing_activity(self):
        stage_id = self.stage_id.id
        if not self.stage_id.is_client_feedback:
            self.sudo().activity_unlink(
                ['kzm_project_base.ticket_closing_activity'])
            self.write({'stage_id': stage_id})
        else:
            self.write({'feedback_date': fields.Date.today()})
            note = _(
                'This Ticket is being in Feedback State since %s Would you linke to close it') % (
                       self.feedback_date)
            if self.user_id:
                if self.feedback_date:
                    self._origin.sudo().activity_schedule('kzm_project_base.ticket_closing_activity',
                                                          self.feedback_date + relativedelta(days=3),
                                                          note=note,
                                                          user_id=self.user_id.id)

    @api.onchange('project_id', 'task_id')
    def _onchange_task_id(self):
        if self.timesheet_ids:
            if self.task_id:
                error_line = "You cannot change the task while there are timesheets"
                raise ValidationError(error_line)

    @api.depends('partner_id')
    def _compute_contract_id(self):
        for rec in self:
            contract = False
            if rec.partner_id:
                contract = rec.env['contract.cadre'].sudo().search(
                    ['|', ('customer_id', '=', rec.partner_id.id), '|',
                     ('secondary_customer_ids', 'in', rec.partner_id.id),
                     ('contact_ids', 'in', rec.partner_id.id),
                     ], order='first_date DESC', limit=1
                )
            rec.contract_id = contract

    @api.depends('partner_id', 'contract_id')
    def _get_domain(self):
        for r in self:
            partners = []
            if r.contract_id:
                if r.contract_id.customer_id:
                    partners.append(r.contract_id.customer_id.id)
                if r.contract_id.secondary_customer_ids:
                    for rec in r.contract_id.secondary_customer_ids:
                        partners.append(rec.id)
                if r.contract_id.contact_ids:
                    for eec in r.contract_id.contact_ids:
                        partners.append(eec.id)
                domain_tasks = [('stage_id.sequence', '=', 1)]
                if partners:
                    domain_tasks += [('partner_id', 'in', partners)]
                r.domain_task = self.env['project.task'].sudo().search(domain_tasks)
            else:
                r.domain_task = False

    @api.constrains('timesheet_ids', 'timesheet_ids.unit_amount', 'estimated_charge')
    def _check_charge_estime_ticket(self):
        for rec in self:
            print("rec._origin", rec._origin)
            timesh = self.env['account.analytic.line'].sudo().search([('helpdesk_ticket_id', '=', rec._origin.id)])
            if timesh:
                timesheet_time = sum(time.unit_amount for time in timesh)
                if timesheet_time > rec.estimated_charge:
                    error_line = "The timesheet exceeds the estimated workload"
                    raise ValidationError(error_line)

    @api.onchange('estimated_charge', 'sold', 'real_charge')
    def check_estimated_charge(self):
        for rec in self:
            if rec.estimated_charge > rec.sold + rec.real_charge:
                raise ValidationError("The estimated workload exceeds the available balance.")

    def unlink(self):
        if len(self.timesheet_ids) >= 1:
            raise ValidationError("You cannot delete a ticket that has a linked timesheet!")
        return super(HelpdeskTicket, self).unlink()

    def affect_ticket(self):
        action = self.env.ref(
            'kzm_project_base.affectation_ticket_action').read()[0]
        return action


class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    is_client_feedback = fields.Boolean(string="Is a feedback stage")
    is_clotured = fields.Boolean(string="Is a closing stage")
