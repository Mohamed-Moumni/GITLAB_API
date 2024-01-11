from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'account.fast.reconcile'
    _description = 'Account Fast Reconcile'
    _rec_name = 'ref_v8'

    ref_v8 = fields.Char(string="Ref V13")
    corresponding_number = fields.Char(string="Corresponding number")
    account_move_line_ids = fields.Many2many('account.move.line')
