# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def cleanup_unreconcile(self):
        # unreconcile
        if self.env['ir.model'].search([('model', '=', 'account.move.line')]):
            move_line_ids = self.env['account.move.line'].search([])
            move_line_ids.remove_move_reconcile()

    def cleanup_invoices(self):
        if self.env['ir.model'].search([('model', '=', 'account.move.line')]):
            # unreconcile
            self.cleanup_unreconcile()
            self.env.cr.execute("""DELETE FROM account_move_line;
                                        DELETE FROM account_move;""")

    def cleanup_payments(self):
        # unreconcile
        if self.env['ir.model'].search([('model', '=', 'account.payment')]):
            self.cleanup_unreconcile()
            self.env.cr.execute(""" DELETE FROM account_payment;""")
            seq_ids = self.env['ir.sequence'].search([])
            seq_ids.write({'number_next_actual': 1})

    def cleanup_stock(self):
        stock = self.env['ir.module.module'].search([('name', '=', 'stock')])
        print("=========>", stock, stock.state)
        if stock and stock.state == 'installed':
            self.env.cr.execute("""
                                DELETE FROM stock_scrap;
                                DELETE FROM stock_quant;
                                DELETE FROM stock_move_line;
                                DELETE FROM stock_move;
                                DELETE FROM stock_valuation_layer;
                                DELETE FROM stock_picking;""")
            seq_ids = self.env['ir.sequence'].search([])
            seq_ids.write({'number_next_actual': 1})

    def cleanup_so(self):
        if self.env['ir.model'].search([('model', '=', 'sale.order')]):
            self.cleanup_invoices()
            self.cleanup_stock()
            sale_order_ids = self.env['sale.order'].search([])
            for so in sale_order_ids:
                so.action_cancel()
            # for so in sale_order_ids:
            #     so.action_draft()
            for so in sale_order_ids:
                so.unlink()
            seq_ids = self.env['ir.sequence'].search([])
            seq_ids.write({'number_next_actual': 1})

    def cleanup_po(self):
        if self.env['ir.model'].search([('model', '=', 'purchase.order')]):
            # cleanup invoices
            self.cleanup_invoices()
            # cleanup stock
            self.cleanup_stock()
            purchase_order_ids = self.env['purchase.order'].search([])
            # cancel PO
            purchase_order_ids.button_cancel()
            # delete PO
            purchase_order_ids.unlink()
            seq_ids = self.env['ir.sequence'].search([])
            seq_ids.write({'number_next_actual': 1})

    def cleanup_so_po(self):
        if self.env['ir.model'].search([('model', '=', 'sale.order')]) and self.env[
            'ir.model'].search([('model', '=', 'purchase.order')]):
            self.cleanup_invoices()
            self.cleanup_stock()
            sale_order_ids = self.env['sale.order'].search([])
            for so in sale_order_ids:
                so.action_cancel()
            for so in sale_order_ids:
                so.action_draft()
            for so in sale_order_ids:
                so.unlink()
            purchase_order_ids = self.env['purchase.order'].search([])
            purchase_order_ids.button_cancel()
            purchase_order_ids.unlink()
            seq_ids = self.env['ir.sequence'].search([])
            seq_ids.write({'number_next_actual': 1})

    def cleanup_production(self):
        if self.env['ir.model'].search([('model', '=', 'mrp.production')]):
            self.env.cr.execute("""
                                DELETE FROM mrp_production;
                                DELETE FROM mrp_workorder;
                                DELETE FROM mrp_unbuild;
                                DELETE FROM stock_scrap;""")

    def cleanup_pos(self):
        if self.env['ir.model'].search([('model', '=', 'pos.order')]):
            self.env.cr.execute("""
                                DELETE FROM pos_payment;
                                DELETE FROM pos_order;
                                DELETE FROM pos_order_line;""")

    def cleanup_all(self):
        # cleanup invoices
        self.cleanup_invoices()
        # cleanup stock
        self.cleanup_stock()
        # cleanup SO PO
        self.cleanup_so_po()
        self.cleanup_production()
        self.cleanup_pos()
        seq_ids = self.env['ir.sequence'].search([])
        seq_ids.write({'number_next_actual': 1})
