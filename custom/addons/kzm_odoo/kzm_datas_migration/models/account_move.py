# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    x_id_ext = fields.Char(string="ID Externe RPC")
    old_ref_lettrage = fields.Char("Ancien référence de lettrage")

    def action_lettrage(self):
        print("UUUUUUU")
        for rec in self:
            if rec.old_ref_lettrage != '' and rec.old_ref_lettrage != 'P':
                for line in rec.line_ids:
                    if line.account_id.account_type == 'asset_receivable' or line.account_id.account_type == 'liability_payable':
                        line.old_ref_lettrage = rec.old_ref_lettrage
