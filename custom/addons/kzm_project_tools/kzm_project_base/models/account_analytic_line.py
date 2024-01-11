from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    contract_id = fields.Many2one('contract.cadre', string=_("Contract Cadre"))
    task_id = fields.Many2one('project.task', string=_("Tache"), compute="_get_task")
    type = fields.Selection([
        ("Abonnement", "Subscription"),
        ("carnet", "Carnet"),
        ("project", "Project")],
        string=_("Type"))

    # @api.constrains('helpdesk_ticket_id', 'unit_amount')
    def _check_unit_amount(self):
        for record in self:
            if record.helpdesk_ticket_id and not record.unit_amount:
                msg = "Impossible de créer TS avec 0 heures passé"
                raise ValidationError(msg)

    @api.onchange('helpdesk_ticket_id', 'unit_amount')
    def _onchange_unit_amount(self):
        for record in self:
            if record.helpdesk_ticket_id and record.helpdesk_ticket_id.stage_id.is_clotured:
                msg = "Impossible de créer TS ou modifier les heures passés sur les tickets clôturés"
                raise ValidationError(msg)

    @api.onchange('unit_amount', 'helpdesk_ticket_id', 'helpdesk_ticket_id.sold')
    def _check_sold_ticket(self):
        for rec in self:
            if rec.helpdesk_ticket_id:
                rec.helpdesk_ticket_id._onchange_real_charge_portal()
                if rec.unit_amount > rec.helpdesk_ticket_id.sold:
                    error_line = "La feuille de temps dépasse le solde disponible"
                    raise ValidationError(error_line)

    @api.constrains('helpdesk_ticket_id.estimated_charge', 'unit_amount')
    def _check_estimated_charge_ticket(self):
        for rec in self:
            if rec.helpdesk_ticket_id:
                if sum([ts.unit_amount for ts in
                        rec.helpdesk_ticket_id.timesheet_ids]) > rec.helpdesk_ticket_id.estimated_charge:
                    error_line = "La feuille de temps dépasse la charge estimée"
                    raise ValidationError(error_line)

    # def write(self, vals):
    #     print("rec", self)
    #     for rec in self:
    #         if rec.helpdesk_ticket_id:
    #             if rec.unit_amount > rec.helpdesk_ticket_id.sold:
    #                 error_line = "La feuille de temps dépasse le solde disponible"
    #                 raise ValidationError(error_line)
    #     super(AccountAnalyticLine, self).write(vals)

    @api.depends('helpdesk_ticket_id', 'helpdesk_ticket_id.task_id')
    def _get_task(self):
        for r in self:
            r.task_id = False
            if r.helpdesk_ticket_id.task_id:
                r.task_id = r.helpdesk_ticket_id.task_id.id

    @api.constrains('task_id', 'helpdesk_ticket_id')
    def _check_no_link_task_and_ticket(self):
        # Check if any timesheets are not linked to a ticket and a task at the same time
        if any(timesheet.task_id and timesheet.helpdesk_ticket_id for timesheet in self):
            return {
                'type': 'ir.actions.client',
                'balise': 'display_notification',
                'paramètres': {
                    'type': 'warning',
                    'title': "Réservation",
                    'message': "Réservation",
                    'collant': False,
                    'suivant': {
                        'type': 'ir.actions.act_window_close'
                    },
                }}

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._check_unit_amount()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._check_unit_amount()
        return res

    def write(self, vals):
        self._check_unit_amount()
        return super().write(vals)
