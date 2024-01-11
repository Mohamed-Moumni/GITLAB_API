# -*- coding: utf-8 -*-
"""Import"""
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class SoldTicketDerogaton(models.Model):
    """ Sold Ticket Derogaton """
    _name = 'sold.ticket.derogation'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'ticket_id'

    existing_charge = fields.Float()
    additional_charge = fields.Float(tracking=True)
    reason = fields.Text()
    state = fields.Selection([('draft', 'Draft'), ('to_validate', 'To Validate'), ('validated', 'Validated')],
                             default='draft')
    ticket_id = fields.Many2one('helpdesk.ticket')
    manager_id = fields.Many2one('res.users', related="ticket_id.contract_id.product_owner")
    not_to_show = fields.Boolean('res.users', compute="_compute_not_to_show")
    task_id = fields.Many2one('project.task', related="ticket_id.task_id")
    contract_id = fields.Many2one('contract.cadre', related="ticket_id.contract_id")

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("You can only delete derogations that are in draft form."))
        return super(SoldTicketDerogaton, self).unlink()

    def _compute_not_to_show(self):
        for record in self:
            record.not_to_show = record.ticket_id.contract_id.product_owner.id == self.env.user.id

    def button_validated(self):
        for record in self:
            somme = record.ticket_id.estimated_charge + record.additional_charge
            # difference = record.task_id.plafond - record.task_id.effective_hours
            # if somme > difference:
            #     raise ValidationError(_("The estimated workload exceeds the available ceiling."))
            record.state = 'validated'
            record.ticket_id.estimated_charge = somme

    def get_actual_page_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action = self.env.ref('kzm_planning.ticket_derogation_menu_action_window')
            link = str(base_url) + '/web#id=' + str(record.id) + '&action=' + str(
                action.id) + '&model=sold.ticket.derogation&view_type=form'
            return link

    def button_to_validate(self):
        for record in self:
            record.state = 'to_validate'
            template_id = self.env.ref('kzm_planning.to_validate_email_template_new').id
            mail_template = self.env['mail.template'].browse(template_id)
            mail_template.send_mail(record.id, force_send=True)
