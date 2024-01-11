# -*- coding: utf-8 -*-

import ast

from odoo import models, fields, _


class ModelName(models.Model):
    _inherit = 'account.mass.reconcile'

    limit = fields.Integer()

    def compute_move_line_ids(self):
        obj_move_line = self.env["account.move.line"]
        reconciled_mv_lines = []
        for fs in self.env['account.fast.reconcile'].search([]):
            reconciled_mv_lines += fs.account_move_line_ids.ids
        lines = obj_move_line.search(
            [("account_id", "=", self.account.id),
             ("old_ref_lettrage", "!=", ""),
             ("parent_state", "=", "posted"),
             ("reconciled", "=", False)]
        )
        group_by_ref = {}
        for l in lines:
            if l.old_ref_lettrage in group_by_ref:
                group_by_ref[l.old_ref_lettrage].append(l)
            else:
                group_by_ref[l.old_ref_lettrage] = [l]

        move_lines = []

        for ref_let in group_by_ref:
            lxxx = group_by_ref[ref_let]
            credit = sum(li.credit for li in lxxx)
            debit = sum(li.debit for li in lxxx)
            # print("------------------>",credit, debit)
            print("==================>", credit - debit)
            print("==================>", len(lxxx) == 2)
            if ((credit - debit) == 0) and len(lxxx) == 2:
                ids = [lx.id for lx in lxxx]
                move_lines.append(ids)

        # print("11111111111111", type(self.ids))
        print("===========================")
        print(move_lines)
        print("===========================")

        return str(move_lines) if move_lines else "[]"

    def custom_reconcile_method(self):
        vals = self.compute_move_line_ids()
        print(range(len(ast.literal_eval(vals))))
        for i in range(len(ast.literal_eval(vals))):
            # obj_move_line.browse(ast.literal_eval(vals)[i]).remove_move_reconcile()
            self.env['account.reconciliation.widget'].process_move_lines(
                [{'id': None, 'type': None, 'mv_line_ids': ast.literal_eval(vals)[i],
                  'new_mv_line_dicts': []}])
            self.env['account.fast.reconcile'].create({
                'ref_v8': self.env['account.move.line'].search(
                    [('id', '=', ast.literal_eval(vals)[i][0])]).old_ref_lettrage,
                'corresponding_number': self.env['account.move.line'].search(
                    [('id', '=', ast.literal_eval(vals)[i][0])]).matching_number,
                'account_move_line_ids': self.env['account.move.line'].search(
                    [('id', 'in', ast.literal_eval(vals)[i])])
            })
        return {
            'name': _('Account fast reconcile lines'),
            'view_type': 'list',
            'view_mode': 'list,form',
            'views': [[self.env.ref('fast_reconcile.account_fast_reconcile_view_tree').id, 'list'],
                      [self.env.ref('fast_reconcile.account_fast_reconcile_view_form').id, 'form']],
            'res_model': 'account.fast.reconcile',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class AccountFastReconcileWizard(models.TransientModel):
    _name = "account.fast.reconcile.wizard"
    _description = "Wizard for fast reconcile"

    limit = fields.Integer(required=True, string="Limit")
    remaining = fields.Integer(string="Remaining move lines")
    move_line_ids = fields.Many2many('account.move.line', string="Account move lines ids to reconcile",
                                     compute="compute_move_line_ids", store=1)
    move_lines = fields.Char(compute="compute_move_line_ids")
    partner_ids = fields.Many2many('res.partner', string="Partners")

    def get_partners(self):
        obj_move_line = self.env["account.move.line"]
        domain = [("old_ref_lettrage", 'not in', ["", False, " "]),
                  ('full_reconcile_id', "=", False),
                  ('date', '<=', '2023-12-31'),
                  ('date', '>=', '2010-01-01'),
                  ('account_id.user_type_id.type', 'in', ['payable', 'receivable'])]
        lines = obj_move_line.search(domain)
        partners = lines.mapped('partner_id')
        return partners

    def custom_compute_move_line_ids(self, partner=False):
        obj_move_line = self.env["account.move.line"]
        domain = [("old_ref_lettrage", 'not in', ["", False, " "]),
                  ('full_reconcile_id', "=", False),
                  ('date', '<=', '2023-12-31'),
                  ('date', '>=', '2010-01-01'),
                  ('account_id.user_type_id.type', 'in', ['payable', 'receivable'])]

        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        if partner:
            domain.append(('partner_id', '=', partner.id))

        lines = obj_move_line.search(domain)

        print("=====================================++++++>", lines)
        group_by_ref_by = {}
        move_lines = []
        for l in lines:
            if l.old_ref_lettrage in group_by_ref_by:
                group_by_ref_by[l.old_ref_lettrage].append(l)
            else:
                group_by_ref_by[l.old_ref_lettrage] = [l]

        # pprint(group_by_ref_by)
        for ref in group_by_ref_by:
            lxxx = group_by_ref_by[ref]
            credit = sum(li.credit for li in lxxx)
            debit = sum(li.debit for li in lxxx)
            print("==================+++++>", ref)
            balance = credit - debit
            print("------------------>", balance)
            if balance == 0:
                ids = [lx.id for lx in lxxx]
                move_lines.append(ids)

        # print("=============>", move_lines)
        if move_lines:
            self.move_lines = move_lines
            self.move_line_ids = [(6, 0, [x for xs in move_lines for x in xs])]
        else:
            self.move_lines = []
            self.move_line_ids = False

        return self.move_lines
        # print("11111111111111", type(self.ids))

    def compute_move_line_ids(self):
        obj_move_line = self.env["account.move.line"]
        reconciled_mv_lines = []
        for fs in self.env['account.fast.reconcile'].search([]):
            reconciled_mv_lines += fs.account_move_line_ids.ids

        lines = obj_move_line.search(
            [
                ("parent_state", "=", "posted"),
                ("old_ref_lettrage", "!=", ""),
                ("id", "not in", reconciled_mv_lines),
            ]
        )
        # if not reconciled_mv_lines:
        #     reconciled_mv_lines = 0
        # else:
        #     reconciled_mv_lines = ','.join([str(x) for x in reconciled_mv_lines])

        # request = "SELECT id, account_id, old_ref_lettrage, credit, debit FROM account_move_line WHERE parent_state = 'posted' AND old_ref_lettrage != '' AND id not in (%s)" % (
        #     reconciled_mv_lines)

        self.remaining = len(lines)
        # ("reconciled", "=", False),
        # print(lines)
        group_by_ref = {}
        for l in lines:
            if l.account_id in group_by_ref:
                group_by_ref[l.account_id].append(l)
            else:
                group_by_ref[l.account_id] = [l]

        # pprint(group_by_ref)
        move_lines = []
        for ref in group_by_ref:
            lines_values = group_by_ref[ref]
            group_by_ref_by = {}
            for l in lines_values:
                if l.old_ref_lettrage in group_by_ref_by:
                    group_by_ref_by[l.old_ref_lettrage].append(l)
                else:
                    group_by_ref_by[l.old_ref_lettrage] = [l]

            for ref_let in group_by_ref_by:
                lxxx = group_by_ref_by[ref_let]
                credit = sum(li.credit for li in lxxx)
                debit = sum(li.debit for li in lxxx)
                # print("------------------>",credit, debit)
                if credit - debit == 0:
                    ref.reconcile = True

                    ids = [lx.id for lx in lxxx]
                    move_lines.append(ids)

        self.move_lines = move_lines
        # print("11111111111111", type(self.ids))
        self.move_line_ids = [(6, 0, [x for xs in move_lines for x in xs])]

    def q_fast_reconcile(self):

        for partner in self.get_partners():
            val = self.custom_compute_move_line_ids(partner)
            self.with_delay().fast_reconcile(val)
        # self.custom_compute_move_line_ids()
        # for i in range(len(ast.literal_eval(self.move_lines))):
        #     self.with_delay().one_fast_reconcile(i, self.move_line_ids)

    def fast_reconcile(self, moves=False):
        # self.compute_move_line_ids()
        # self.custom_compute_move_line_ids()
        if not moves:
            moves = self.move_lines
        for i in range(len(ast.literal_eval(moves))):
            # obj_move_line.browse(ast.literal_eval(self.move_lines)[i]).remove_move_reconcile()
            try:
                self.env['account.reconciliation.widget'].process_move_lines(
                    [{'id': None, 'type': None, 'mv_line_ids': ast.literal_eval(moves)[i],
                      'new_mv_line_dicts': []}])
                self.env['account.fast.reconcile'].create({
                    'ref_v8': self.env['account.move.line'].search(
                        [('id', '=', ast.literal_eval(moves)[i][0])]).old_ref_lettrage,
                    'corresponding_number': self.env['account.move.line'].search(
                        [('id', '=', ast.literal_eval(moves)[i][0])]).matching_number,
                    'account_move_line_ids': self.env['account.move.line'].search(
                        [('id', 'in', ast.literal_eval(moves)[i])])
                })
            except Exception as e:
                pass
        return {
            'name': _('Account fast reconcile lines'),
            'view_type': 'list',
            'view_mode': 'list,form',
            'views': [[self.env.ref('fast_reconcile.account_fast_reconcile_view_tree').id, 'list'],
                      [self.env.ref('fast_reconcile.account_fast_reconcile_view_form').id, 'form']],
            'res_model': 'account.fast.reconcile',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def one_fast_reconcile(self, i, lines):
        try:
            self.env['account.reconciliation.widget'].process_move_lines(
                [{'id': None, 'type': None, 'mv_line_ids': ast.literal_eval(lines)[i],
                  'new_mv_line_dicts': []}])
            self.env['account.fast.reconcile'].create({
                'ref_v8': self.env['account.move.line'].search(
                    [('id', '=', ast.literal_eval(lines)[i][0])]).old_ref_lettrage,
                'corresponding_number': self.env['account.move.line'].search(
                    [('id', '=', ast.literal_eval(lines)[i][0])]).matching_number,
                'account_move_line_ids': self.env['account.move.line'].search(
                    [('id', 'in', ast.literal_eval(lines)[i])])
            })
        except Exception as e:
            pass
