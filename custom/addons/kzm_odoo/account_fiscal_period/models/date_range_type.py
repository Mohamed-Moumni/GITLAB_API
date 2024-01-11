# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DateRangeType(models.Model):
    _inherit = "date.range.type"

    fiscal_period = fields.Boolean(string='Is fiscal period ?', default=False, compute='_compute_fiscal_period',
                                   store=1)
    kzm_is_quinzaine = fields.Boolean("Is quizaine", compute='_compute_fiscal_period', store=1)

    @api.constrains('unit_of_time')
    def _compute_fiscal_period(self):
        for rec in self:
            rec.fiscal_period = rec.unit_of_time != '0'
            rec.kzm_is_quinzaine = (rec.unit_of_time == '3' and rec.duration_count == 15)

    # def unlink(self):
    #     """
    #     Cannot delete a date_range_type with 'fiscal_period' flag = True
    #     """
    #     for rec in self:
    #         if rec.fiscal_period:
    #             raise exceptions.ValidationError(
    #                 ('Vous ne pouvez pas supprimer un type de flag fiscal_year"')
    #             )
    #         else:
    #             super(DateRangeType, rec).unlink()
