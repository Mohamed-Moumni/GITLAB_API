# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _default_user(self):
        if self.env.user.has_group('project.group_project_user') and not self.env.user.has_group(
                'project.group_project_manager'):
            return True
        else:
            return False

    def _get_default_custom_tag_ids(self):
        project_id = self.env.context.get('default_project_id', False)
        project_id = self.env['project.project'].browse(project_id)
        return project_id.custom_tag_ids if project_id else False

    type = fields.Selection([
        ("carnet", "Carnet"),
        ("Abonnement", "Subscription"),
        ("project", "Project")],
        string=_("Type"), compute='_get_type', store=1)
    contract_id = fields.Many2one('contract.cadre', string=_("Contrat Cadre"), readonly=0, compute="_get_contract",
                                  domain="['|',('customer_id', '=', partner_id),('secondary_customer_ids', 'in', partner_id)]",
                                  store=1)
    carnet_id = fields.Many2one('project.carnet', store=1, string=_("Carnet"))
    sale_id = fields.Many2one('sale.order', string=_("Order"), readonly=1)
    sold = fields.Float(string=_("Solde"), compute="_get_sold")
    timesheet_ids = fields.One2many('account.analytic.line', 'task_id', string=_("Feuilles de temps"))
    ticket_ids = fields.One2many('helpdesk.ticket', 'task_id', string=_("Tickets"))
    is_user = fields.Boolean(compute="_diff_user", default=_default_user)
    user_ids = fields.Many2many(compute="_get_user_id", readonly=0)
    sold_derogation_count = fields.Integer(compute="_elements_count", string=_("Number of sold derogation"))
    ticket_count = fields.Integer(compute="_elements_count", string=_("Number of tickets"))
    plafond = fields.Float(string=_("Plafond"))
    user_has_edit_plafond = fields.Boolean(compute="_compute_user_has_edit_plafond", store=False)
    custom_tag_ids = fields.Many2many('custom.project.tags', 'task_custom_tags_rel', string="Consignes",
                                      default=_get_default_custom_tag_ids)

    def _compute_user_has_edit_plafond(self):
        for record in self:
            record.user_has_edit_plafond = self.env.user.has_group('kzm_project_base.group_edit_plafond')

    @api.constrains('planned_hours', 'plafond')
    def _check_planned_hours(self):
        for record in self:
            if record.plafond < record.planned_hours:
                msg = f"Les heures allouées ({'%.2f' % record.planned_hours}) de la tâche '{record.name}' est "
                msg += f"supérieure au plafond ({'%.2f' % record.plafond})"
                raise ValidationError(msg)

    @api.depends('ticket_ids')
    def _elements_count(self):
        for r in self:
            sold_derogation = self.env['sold.task.derogation'].search([('task_id', '=', r.id)])
            r.sold_derogation_count = len(sold_derogation)
            r.ticket_count = len(self.ticket_ids)

    @api.depends('contract_id.product_owner')
    def _get_user_id(self):
        for r in self:
            if r.contract_id.product_owner:
                r.user_ids = [r.contract_id.product_owner.id]

    def _diff_user(self):
        self.is_user = False
        if self.env.user.has_group('project.group_project_user') and not self.env.user.has_group(
                'project.group_project_manager'):
            self.is_user = True

    @api.depends('planned_hours', 'effective_hours')
    def _get_sold(self):
        for r in self:
            r.sold = r.planned_hours - r.effective_hours

    @api.depends('sale_line_id', 'sale_line_id.product_id.service_tracking')
    def _get_type(self):
        for r in self:
            if r.sale_line_id and r.sale_line_id.product_id.service_tracking == 'task_global_project' and r.sale_line_id.product_id.type_1 == 'autre':
                r.type = "Abonnement"
            elif r.sale_line_id and r.sale_line_id.product_id.service_tracking == 'task_in_project' and r.sale_line_id.product_id.type_1 == 'autre':
                r.type = "project"
            elif r.sale_line_id and r.sale_line_id.product_id.type_1 == 'carnet':
                r.type = "carnet"

    @api.depends('partner_id')
    def _get_contract(self):
        for r in self:
            r.contract_id = False
            if r.partner_id:
                contract = r.env['contract.cadre'].sudo().search(
                    ['|', ('customer_id', '=', r.partner_id.id),
                     ('secondary_customer_ids', 'in', r.partner_id.id),
                     ], order='first_date DESC', limit=1
                )
                r.contract_id = contract

    def unlink(self):
        if len(self.ticket_ids) >= 1:
            raise ValidationError("Vous ne pouvez pas supprimer une tâche ayant un ticket lié!")
        return super(ProjectTask, self).unlink()

    def get_sold_derogation(self):
        return {
            "name": _("Sold derogation"),
            "type": "ir.actions.act_window",
            "res_model": "sold.task.derogation",
            "view_mode": "tree,form",
            "domain": [("task_id", "=", self.id)],
            "context": {"default_task_id": self.id},
        }

    def get_all_ticket(self):
        return {
            "name": _("Tickets"),
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.ticket_ids.ids)],
            "context": {"default_task_id": self.id},
        }

    @api.model
    def create(self, vals):
        if not vals.get('plafond', 0) and (planned_hours := vals.get('planned_hours', 0)) > 0:
            partner_id = self.env['res.partner'].sudo().browse(vals.get('partner_id'))
            sale_line_id = self.env['sale.order.line'].sudo().browse(vals.get('sale_line_id'))
            vals['plafond'] = planned_hours
            vals['planned_hours'] = 0
            vals['name'] = f"{partner_id.name} - {sale_line_id.product_id.name} ({sale_line_id.order_id.name})"

        return super().create(vals)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_id = fields.Many2one('sale.order', string=_("Order"), readonly=1, store=1)
    contract_id = fields.Many2one('contract.cadre', string=_("Contrat Cadre"), readonly=1, compute="_get_contract",
                                  store=1)
    is_abonnement = fields.Boolean(string="Est abonnement")
    collective_project = fields.Boolean(string=_("Collective project"))
    ticket_count = fields.Integer(compute="_elements_count", string=_("Number of tickets"))
    custom_tag_ids = fields.Many2many('custom.project.tags', 'project_custom_tags_rel', string="Consignes")

    @api.depends('ticket_ids')
    def _elements_count(self):
        for r in self:
            r.ticket_count = len(self.ticket_ids)

    @api.depends('sale_id', 'sale_order_id')
    def _get_contract(self):
        for r in self:
            r.contract_id = False
            if r.sale_order_id:
                r.contract_id = r.sale_order_id.contract_id.id
                r.partner_id = r.sale_order_id.partner_id.id
            elif r.partner_id:
                contract = r.env['contract.cadre'].sudo().search(
                    ['|', ('customer_id', '=', r.partner_id.id),
                     ('secondary_customer_ids', 'in', r.partner_id.id),
                     ], order='first_date DESC', limit=1
                )
                r.contract_id = contract

    def unlink(self):
        if self.task_count >= 1:
            raise ValidationError("Vous ne pouvez pas supprimer un projet ayant une tâche liée!")
        return super(ProjectProject, self).unlink()

    def open_tasks(self):
        self.ensure_one()
        return {
            'name': _('Tasks'),
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.task_ids.ids)],
            'context': {'default_project_id': self.id},
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def get_all_ticket(self):
        return {
            "name": _("Tickets"),
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.ticket_ids.ids)],
            "context": {"default_project_id": self.id},
        }

    @api.model
    def create(self, vals):
        state = self.env['project.task.type'].search([('user_id', '=', False)])
        vals['type_ids'] = state.ids
        res = super(ProjectProject, self).create(vals)
        return res
