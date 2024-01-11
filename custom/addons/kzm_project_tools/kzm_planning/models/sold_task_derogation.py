# -*- coding: utf-8 -*-
"""Import"""
from odoo import models


class SoldTaskDerogation(models.Model):
    """ Sold task derogation """
    _inherit = 'sold.task.derogation'

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
        if self.state == 'on_hold':
            self.task_id.plafond += self.estimated_time
            self.task_id.planned_hours += self.estimated_time
            self.state = 'validated'
