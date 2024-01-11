# -*- coding: utf-8 -*-

from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime, date

class StageProject(models.Model):
    _name = 'project.stage'
    _order = 'avancement'

    name = fields.Char(string="name")
    avancement = fields.Integer("Avancement")
    fold = fields.Boolean("Folded in Pipeline")


class LotEval(models.Model):
    _name = 'project.lot'

    @api.depends('lot_eval_line_ids', 'task_ids', 'task_ids.stage_id', 'task_ids.planned_hours',
                 'task_ids.effective_hours')
    def _compute_charges(self):
        for o in self:
            planned_tasks = o.task_ids.filtered(lambda r: r.stage_id.is_planned)
            progress_tasks = o.task_ids.filtered(lambda r: r.stage_id.is_progress)
            o.estimated_charges = sum([l.estim_charges for l in o.lot_eval_line_ids])
            o.planned_charges = sum([l.planned_hours for l in planned_tasks])
            o.realised_charges = sum([l.effective_hours for l in o.task_ids])
            #o.advancement = float(o.realised_charges) / (o.estimated_charges or 1)
            o.advancement = 0 if not o.estimated_charges else round(100.0 * (o.realised_charges) / o.estimated_charges,
                                                                    2)
            if o.estimated_charges == 0:
                o.advancement = 0

    # @api.depends('template_lot_id')
    # def _get_com_name(self):
    #     for o in self:
    #         o.name = o.template_lot_id and o.template_lot_id.name or ''

    # = fields.Char('Name', compute=_get_com_name)
    name = fields.Char('Name')
    date_start = fields.Date('Date beginning')
    date_end = fields.Date('Date end')
    planned_charges = fields.Float("Planned charges", compute=_compute_charges)
    estimated_charges = fields.Float("Estimated charges", compute=_compute_charges)
    realised_charges = fields.Float("Realised charges", compute=_compute_charges, store=True)
    advancement = fields.Float("Advancement", compute=_compute_charges)

    resp_tech_id = fields.Many2one("hr.employee", "Technique responsible")
    resp_fonc_id = fields.Many2one("hr.employee", "Functional responsible")
    resp_tech_user_id = fields.Many2one("res.users", related="resp_tech_id.user_id", string="User technique")
    resp_fonc_user_id = fields.Many2one("res.users", related="resp_fonc_id.user_id", string="User technique")

    project_id = fields.Many2one('project.project', string='Project')
    #template_lot_id = fields.Many2one('project.template.lot', string='Name')

    lot_eval_line_ids = fields.One2many('project.lot.line', 'lot_id', 'Lot lines')
    task_ids = fields.One2many('project.task', 'lot_id', 'Tasks')


class LotLineEval(models.Model):
    _name = 'project.lot.line'

    name = fields.Char("Name", required=True)
    estim_charges = fields.Float("Estimated charge (hours)")
    estim_charges_dy = fields.Float("Estimated charge (days)")
    lot_id = fields.Many2one('project.lot', string='Lot', required=True)
    project_id = fields.Many2one('project.project', related='lot_id.project_id', string='Project')

    @api.onchange("estim_charges")
    def on_change_estim_charges(self):
        hr_per_day = self.env.user.company_id and self.env.user.company_id.hrs_per_day or 8.0
        for o in self:
            o.estim_charges_dy = float(o.estim_charges or 0) / float(hr_per_day or 8.0)

    @api.onchange("estim_charges_dy")
    def on_change_estim_charges_dy(self):
        hr_per_day = self.env.user.company_id and self.env.user.company_id.hrs_per_day or 8.0
        for o in self:
            o.estim_charges = float(o.estim_charges_dy or 0) * float(hr_per_day or 8.0)


# class TemplateLotEval(models.Model):
#     _name = 'project.template.lot'
#     _order = 'sequence'
#
#     name = fields.Char("Name", required=True)
#     sequence = fields.Integer("Sequence", default=5)
#     lot_ids = fields.One2many('project.lot', 'template_lot_id', string='Lots')


class TemplatePhaseEval(models.Model):
    _name = 'project.template.phase'
    _order = 'sequence'

    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Sequence", default=5)
    auto_load = fields.Boolean("Defaut Load", default=False)
    phase_ids = fields.One2many('project.phase', 'template_phase_id', string='Phases')


class ProjectPhase(models.Model):
    _name = 'project.phase'
    _order = 'sequence'

    @api.depends('task_ids')
    def _compute_charges(self):
        for o in self:
            o.estimated_charges = sum([l.planned_hours for l in o.task_ids])
            o.realised_charges = sum([l.effective_hours for l in o.task_ids])
            advancement = 0 if not o.charge_qty else round(100.0 * (o.realised_charges) / o.charge_qty, 2)
            o.advancement = advancement
            o.overtaking = True if advancement > 100 else False

    def _compute_time_delay(self):
        for o in self:
            o.time_delay = 0
            o.is_late = False
            if o.date_end and o.date_end_scheduled:
                time_delay = (fields.Date.from_string(o.date_end) - fields.Date.from_string(o.date_end_scheduled)).days
                o.time_delay = time_delay
                if time_delay > 0:
                    o.is_late = True
            elif o.date_end_scheduled:
                today_delay = (date.today() - fields.Date.from_string(o.date_end_scheduled)).days
                o.is_late = True if today_delay > 0 else False


    @api.depends('template_phase_id')
    def _get_com_name(self):
        for o in self:
            o.name = o.template_phase_id and o.template_phase_id.name or ''

    name = fields.Char("Name", compute=_get_com_name, store=True)
    charge_qty = fields.Float("Charge (Qty)")
    date_start = fields.Date('Date beginning')
    date_end = fields.Date('Date end')

    date_start_scheduled = fields.Date('Scheduled start date')
    date_end_scheduled = fields.Date('Scheduled start date')
    time_delay = fields.Integer('Delay time', compute=_compute_time_delay)
    is_late = fields.Boolean('Is late', compute=_compute_time_delay)
    overtaking = fields.Boolean('Overtaking', compute=_compute_charges)

    estimated_charges = fields.Float("Estimated charges", compute=_compute_charges)
    realised_charges = fields.Float("Realised charges", compute=_compute_charges)
    advancement = fields.Float("Advancement", compute=_compute_charges)

    project_id = fields.Many2one('project.project', string='Project')
    template_phase_id = fields.Many2one('project.template.phase', string='Name')
    task_ids = fields.One2many('project.task', 'phase_id', string='Tasks')
    sequence = fields.Integer("Sequence", related="template_phase_id.sequence")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    lot_id = fields.Many2one('project.lot', 'Lot')
    phase_id = fields.Many2one('project.phase', 'Phase')

    is_progress = fields.Boolean("Is progress", related="stage_id.is_progress")
    is_planned = fields.Boolean("Is Planned", related="stage_id.is_planned")


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _inherits = {'account.analytic.account': "analytic_account_id"}

    def _default_stage(self):
        return self.env['project.stage'].search([], limit=1).id or False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    @api.depends('sale_order_ids', 'account_inv_ids', 'account_inv_ids.amount_untaxed', 'account_inv_ids.state',
                 'lot_ids', 'lot_ids.realised_charges','task_ids', 'lot_ids.lot_eval_line_ids.estim_charges','task_ids.effective_hours','line_ids')
    def _compute_charges(self):
        for o in self:
            hr_day = float(o.company_id.hrs_per_day or 8.0)
            estimated_charges = sum([l.estimated_charges for l in o.sudo().lot_ids])
            o.estimated_charges = estimated_charges
            o.estimated_charges_dy = float(estimated_charges) / hr_day

            # o.planned_charges = sum([l.planned_hours for l in o.task_ids])
            # o.realised_charges = sum([l.effective_hours for l in o.task_ids])
            planned_charges = sum([l.planned_charges for l in o.sudo().lot_ids])
            o.planned_charges = planned_charges
            o.planned_charges_dy = float(planned_charges) / hr_day
            realised_charges = sum([l.unit_amount for l in o.line_ids])

            o.realised_charges = realised_charges
            o.realised_charges_dy = float(realised_charges) / hr_day

            o.advancement = (
                                0 if not o.estimated_charges else (
                                float(o.realised_charges) / o.estimated_charges)) * 100.0
            ordered_amount = sum(
                [l.amount_untaxed for l in o.sudo().sale_order_ids])  # if l.state in ['sale', 'done']])
            invoiced_amount = sum([l.amount_untaxed for l in o.sudo().account_inv_ids if l.state in ['paid', 'open']])
            #o.ordered_amount = ordered_amount

            o.invoiced_amount = o.invoiced_amount
            o.advancement_inv = ((float(invoiced_amount) / float(
                ordered_amount or 1.0)) if ordered_amount > 0 else 0) * 100.0
            # o.hours_budgets = ordered_amount / (o.estimated_charges or 1.0)
            # o.day_budgets = ordered_amount / (o.estimated_charges or 1.0) * hr_day
            # if o.estimated_charges == 0:
            #     o.hours_budgets = 0
            #     o.day_budgets = 0

    def _compute_counts_lot_phase(self):
        for o in self:
            o.lots_count = len(o.sudo().lot_ids)
            o.phases_count = len(o.sudo().phase_ids)
            o.sale_orders_count = len(o.sudo().sale_order_ids)
            o.account_inv_count = len(o.sudo().account_inv_ids)

    def get_phase(self):
        #for o in self:
        phase_template = self.env['project.template.phase'].search([('auto_load','=',True)])
        phase = self.env['project.phase']
        for pt in phase_template:
            phase |= phase.new({'template_phase_id': pt.id})
        self.phase_ids = phase


    @api.constrains('phase_ids')
    def _check_parent_id(self):
        for o in self:
            #list(set([line.product_id.code_sh.id for line in self.sale_picking_line_ids]))
            unique_phase = list(set([line.template_phase_id.id for line in self.phase_ids]))
            phase = list([line.template_phase_id.id for line in self.phase_ids])
            if len(unique_phase)!= len(phase):
                raise ValidationError(_('Error ! two phases with same name'))

    phase_ids = fields.One2many('project.phase', 'project_id', 'Phases')
    lot_ids = fields.One2many('project.lot', 'project_id', 'Lots')
    lot_line_ids = fields.One2many('project.lot.line', 'project_id', 'Lots lines')
    sale_order_ids = fields.One2many('sale.order', 'our_project_id', 'Sales order')
    account_inv_ids = fields.One2many('account.invoice', 'project_id', 'Invoices')

    planned_charges = fields.Float("Planned charges (Hours)", compute=_compute_charges, store=True)
    planned_charges_dy = fields.Float("Planned charges (day)", compute=_compute_charges, store=True)
    estimated_charges = fields.Float("Estimated charges (Hours)", compute=_compute_charges, store=True)
    estimated_charges_dy = fields.Float("Estimated charges (day)", compute=_compute_charges, store=True)
    realised_charges = fields.Float("Realised charges (Hours)", compute=_compute_charges, store=True)
    realised_charges_dy = fields.Float("Realised charges (day)", compute=_compute_charges, store=True)
    advancement_inv = fields.Float("Advancement Facturation", compute=_compute_charges, store=True)
    ordered_amount = fields.Float("Ordered untaxed amount")
    invoiced_amount = fields.Float("Invoiced untaxed amount", compute=_compute_charges, store=True)
    advancement = fields.Float("Advancement", compute=_compute_charges, store=True)
    hours_budgets = fields.Float("THM", readonly=True)
    day_budgets = fields.Float("TJM", readonly=True)

    lots_count = fields.Integer('Lots', default=0, compute=_compute_counts_lot_phase)
    phases_count = fields.Integer('Phases', default=0, compute=_compute_counts_lot_phase)
    sale_orders_count = fields.Integer('Sale orders', default=0, compute=_compute_counts_lot_phase)
    account_inv_count = fields.Integer('Invoices', default=0, compute=_compute_counts_lot_phase)

    stage_id = fields.Many2one("project.stage",string="Etape", default=_default_stage, group_expand='_read_group_stage_ids')

    @api.onchange('sale_order_ids')
    def onchange_ordered_amount(self):
        for o in self :
            hr_day = float(o.company_id.hrs_per_day or 8.0)
            ordered_amount = sum(
                [l.amount_untaxed for l in o.sudo().sale_order_ids])  # if l.state in ['sale', 'done']])
            o.ordered_amount = ordered_amount
            o.hours_budgets = ordered_amount / (o.estimated_charges or 1.0)
            o.day_budgets = ordered_amount / (o.estimated_charges or 1.0) * hr_day
            if o.estimated_charges == 0:
                o.hours_budgets = 0
                o.day_budgets = 0

    @api.model
    def update_all_projects_charges(self):
        self.search([])._compute_charges()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    our_project_id = fields.Many2one('project.project', string='Project')

    @api.onchange('our_project_id')
    def _get_partner_if_none(self):
        for o in self:
            if not o.partner_id:
                if o.our_project_id:
                    o.partner_id = o.our_project_id.partner_id
                    o.onchange_partner_id()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_tots_hours(self):
        for o in self:
            timesh = self.env['account.analytic.line'].search([('task_id', '!=', False), ('employee_id', '=', o.id)])
            time_planned_tasks = timesh.filtered(lambda r: r.task_id.stage_id.is_planned)
            time_progress_tasks = timesh.filtered(lambda r: r.task_id.stage_id.is_progress)
            o.tot_planned = sum([l.unit_amount for l in time_planned_tasks])
            o.tot_in_progress = sum([l.unit_amount for l in time_progress_tasks])

    tot_in_progress = fields.Integer("In progress total", compute=_compute_tots_hours)
    tot_planned = fields.Float("Planned total", compute=_compute_tots_hours)


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_progress = fields.Boolean("Is progress", default=False)
    is_planned = fields.Boolean("Is Planned", default=False)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('origin')
    def _compute_project_origin(self):
        for o in self:
            origin = o.origin
            if origin:
                sales = self.env['sale.order'].search([('name', '=', origin)])
                if sales:
                    sale = sales[0]
                    o.project_id = sale.our_project_id
                else:
                    o.project_id = False
            else:
                o.project_id = False

    project_id = fields.Many2one('project.project', string='Project', compute='_compute_project_origin', store=True)


"""class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('unit_amount', 'employee_id', 'date')
    def contraint_time_sheet(self):
        for o in self:
            if o.task_id and not o.task_id.stage_id.is_progress:
                raise ValidationError(_("You can't create or update a timesheet not in progress"))"""
