# -*- coding: utf-8 -*-
from odoo import models, _, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        group_system_id = self.env['ir.model.data']._xmlid_to_res_id('base.group_system')
        group_system = self.env['res.groups'].browse(group_system_id)
        user_id = self.env.user.id
        if user_id not in group_system.users.ids:
            for values in vals_list:
                if 'groups_id' in values:
                    user = self.new(values)
                    gs = user.groups_id._origin.ids
                    if group_system_id in gs:
                        raise ValidationError(
                            _("You're not able to create a user with settings rule")
                        )
        res = super(ResUsers, self).create(vals_list)
        return res

    def write(self, values):
        group_system_id = self.env['ir.model.data']._xmlid_to_res_id('base.group_system')
        group_system = self.env['res.groups'].browse(group_system_id)
        user_id = self.env.user.id
        if user_id not in group_system.users.ids:
            if values.get('sel_groups_2_4'):
                if values.get('sel_groups_2_4') == 4:
                    raise ValidationError(
                        _("You're not able to switch to settings rule")
                    )
        res = super(ResUsers, self).write(values)
        return res
