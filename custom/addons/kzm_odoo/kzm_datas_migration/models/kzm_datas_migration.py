# -*- coding: utf-8 -*-

import xmlrpc.client
import ast
import logging
from pprint import pprint

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class KzmDatasMigration(models.Model):
    _name = "kzm.datas.migration"
    _description = 'Kzm Datas Migration'
    _rec_name = "model_to_synchronize"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    url = fields.Char(string="URL")
    login = fields.Char(string="Login")
    pwd = fields.Char(string="Password")
    db_name = fields.Char(string="Database Name")
    model_to_synchronize = fields.Many2one('ir.model', 'Model to Synchronize')
    model_to_synchronize_equiv = fields.Char(compute='_compute_model_to_synchronize_equiv',
                                             inverse="_inverse_model_to_synchronize_equiv")
    synch_operation = fields.Selection([
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete")
    ],
        default="create", )

    condition = fields.Char()
    fields_to_synchronize = fields.Many2many('ir.model.fields', domain="[('model_id', '=', model_to_synchronize)]")
    res_model = fields.Char(compute="_compute_res_model", store=1)
    synchronization_key = fields.Many2one('ir.model.fields', domain="[('model_id', '=', model_to_synchronize)]")
    nbr_facture = fields.Integer(string="Nombre d'enregistrements", readonly=True)

    @api.depends('model_to_synchronize')
    def _compute_model_to_synchronize_equiv(self):
        for rec in self:
            rec.model_to_synchronize_equiv = rec.model_to_synchronize.model

    @api.depends('model_to_synchronize')
    def _compute_res_model(self):
        for rec in self:
            rec.res_model = rec.model_to_synchronize.model

    def _inverse_model_to_synchronize_equiv(self):
        pass

    def synch_pj(self):
        # print('eee')
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
        # --------------------- FORMAT DOMAIN ------------------------
        domain = []
        condition = []

        if self.condition:
            x = self.condition
            condition = ast.literal_eval(x)
            # print("RRR", condition)
            if len(condition) == 1:
                domain.append([])
                for i in condition[0]:
                    domain[0].append(i)

            elif len(condition) > 1:
                for i in condition[1:]:
                    s = []
                    for j in i:
                        s.append(j)
                    domain.append(s)
        index_to_del = False
        for i in range(len(domain)):
            if domain[i] == ['&']:

                index_to_del = i

        for i in range(len(domain)):
            # print(domain[i])
            if domain[i] == ['&']:
                index_to_del = i

        if index_to_del:
            domain.pop(index_to_del)

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 self.model_to_synchronize_equiv, 'search_read',
                                 [domain],
                                 {'fields': ['id']})
        _logger.info("========= ACC MOVES RECORDS ============")
        _logger.info(records)
        if records:
            for rec in records:
                pj_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                            'ir.attachment', 'search_read',
                                            [[
                                                ['res_id', '=', rec['id']],
                                                ['res_model', '=', 'account.move']
                                            ]],
                                            {'fields': ['id', 'type', 'datas', 'name']})

                _logger.info("========= ATTACHMENT RECORDS ============")
                _logger.info(pj_records)
                if pj_records:
                    for pj_rec in pj_records:
                        acc_moves = self.env['account.move'].search([
                            ('x_id_ext', '=', rec['id'])
                        ])
                        _logger.info("========= RELATED ACC MOVES RECORDS IN NEW DB V16  ============")
                        _logger.info(pj_records)
                        for acc_move in acc_moves:
                            attachment = self.env['ir.attachment'].create({
                                'name': pj_rec['name'],
                                'type': pj_rec['type'],
                                'datas': pj_rec['datas'],
                                'store_fname': pj_rec['name'],
                                'res_id': acc_move.id,
                                'res_model': 'account.move',
                            })

    def test_connexion(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        try:
            uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
            if uid:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Connection Test Successful!",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Connection Test Failed!",
                        'type': 'danger',
                        'sticky': False,
                    }
                }

        except Exception as ee:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Connection Test Failed!",
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def count_number(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
        # print(condition)
        self.sync_uom()
        # --------------------- FORMAT DOMAIN ------------------------
        domain = []
        condition = []

        if self.condition:
            x = self.condition
            condition = ast.literal_eval(x)
            # print("RRR", condition)
            if len(condition) == 1:
                domain.append([])
                for i in condition[0]:
                    domain[0].append(i)

            elif len(condition) > 1:
                for i in condition[1:]:
                    s = []
                    for j in i:
                        # print(j)
                        s.append(j)
                    domain.append(s)
        index_to_del = False
        for i in range(len(domain)):
            # print(domain[i])
            if domain[i] == ['&']:
                index_to_del = i

        for i in range(len(domain)):
            # print(domain[i])
            if domain[i] == ['&']:
                index_to_del = i

        if index_to_del:
            domain.pop(index_to_del)

        # print("NEW ==> ", domain)

        fields_to_synch = self.fields_to_synchronize.mapped("name")
        if self.model_to_synchronize.model == 'account.move':
            if 'move_type' in fields_to_synch:
                index = fields_to_synch.index('move_type')
                fields_to_synch[index] = 'type'

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 self.model_to_synchronize_equiv, 'search_read',
                                 [domain],
                                 {'fields': fields_to_synch})
        self.nbr_facture = len(records)

    def create_records(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
        # print(condition)
        self.sync_uom()
        # --------------------- FORMAT DOMAIN ------------------------
        domain = []
        condition = []

        if self.condition:
            x = self.condition
            condition = ast.literal_eval(x)
            # print("RRR", condition)
            if len(condition) == 1:
                domain.append([])
                for i in condition[0]:
                    domain[0].append(i)

            elif len(condition) > 1:
                for i in condition[1:]:
                    s = []
                    for j in i:
                        # print(j)
                        s.append(j)
                    domain.append(s)
        index_to_del = False
        for i in range(len(domain)):
            # print(domain[i])
            if domain[i] == ['&']:
                index_to_del = i

        for i in range(len(domain)):
            # print(domain[i])
            if domain[i] == ['&']:
                index_to_del = i

        if index_to_del:
            domain.pop(index_to_del)

        # print("NEW ==> ", domain)
        _logger.info("========= DOMAINE ============")
        _logger.info(domain)

        fields_to_synch = self.fields_to_synchronize.mapped("name")
        fields_to_synch.append('line_ids')

        # print("===> ", fields_to_synch)
        if self.model_to_synchronize.model == 'account.move':
            if 'move_type' in fields_to_synch:
                index = fields_to_synch.index('move_type')
                fields_to_synch[index] = 'type'

        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                 self.model_to_synchronize_equiv, 'search_read',
                                 [domain],
                                 {'fields': fields_to_synch})

        l_data = []
        for rec1 in records:
            data_to_create = {
                "x_id_ext": rec1['id']
            }
            for r1 in rec1:
                val = self.adapt_fields(self.model_to_synchronize, r1, rec1[r1])
                if val:
                    data_to_create.update(val)
            l_data.append(data_to_create)

        if self.model_to_synchronize.model == 'account.move':
            for r in l_data:
                if "type" in r:
                    r['move_type'] = r['type']
                    del r['type']

        if self.model_to_synchronize.model == 'account.move.line':
            for r in l_data:
                if "display_type" in r:
                    if not r['display_type']:
                        r['display_type'] = 'product'

        # print("AAA ", l_data)
        _logger.info("========= DIC FACTURE/PIECE ============")
        _logger.info(l_data)

        # --------------------------------------------

        try:

            if self.synch_operation == "create":
                for rec in l_data:
                    # invoice_id = self.env[self.model_to_synchronize.model].create(rec)
                    _logger.info("========= CREATION FACTURE ===========")
                    # print("RECORD ==> ", rec)
                    if 'partner_id' in rec:
                        if not rec['partner_id']:
                            acc_move = mod.execute_kw(self.db_name, uid, self.pwd,
                                                      'account.move', 'search_read',
                                                      [[['id', '=', rec['x_id_ext']]]],
                                                      {'fields': ['name', 'partner_id']})

                            if acc_move[0]['partner_id']:
                                partner_rec = mod.execute_kw(self.db_name, uid, self.pwd,
                                                             'res.partner', 'search_read',
                                                             [[['id', '=', acc_move[0]['partner_id'][0]]]],
                                                             {'fields': ['name', 'company_type', 'street', 'street2',
                                                                         'city', 'vat', 'email', 'ice', 'ref']})

                                # =============================

                                partner_id = self.env['res.partner'].create(partner_rec[0])

                                rec['partner_id'] = partner_id.id

                    if rec['move_type'] == 'entry':
                        # print("Move type ===> ", rec['move_type'])
                        _logger.info("========= INVOICE LINE (PIECE COMPTABLE)============")
                        # print(rec['line_ids'])
                        list_move_lines = []
                        if rec['line_ids']:
                            for l in rec['line_ids']:
                                records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                         'account.move.line', 'search_read',
                                                         [[['id', '=', l],
                                                           # ['exclude_from_invoice_tab', '=', False],
                                                           ['display_type', '=', False]
                                                           ]],
                                                         {'fields': ['name', 'product_id', 'account_id', 'quantity',
                                                                     'price_unit', 'discount', 'tax_ids',
                                                                     'product_uom_id',
                                                                     'display_type', 'debit', 'credit',
                                                                     'full_reconcile_id']})
                                # print("EE==> ", records)
                                records[0]['display_type'] = 'product'
                                records[0]['x_id_ext'] = records[0]['id']
                                del records[0]['id']
                                if records[0]['account_id']:
                                    cor_val = self.env['account.account'].search([
                                        ('x_id_ext', '=', records[0]['account_id'][0])
                                    ], limit=1)
                                    if cor_val:
                                        records[0]['account_id'] = cor_val.id
                                    else:
                                        records[0]['account_id'] = False

                                if records[0]['product_id']:
                                    cor_val = self.env['product.product'].search([
                                        ('x_id_ext', '=', records[0]['product_id'][0])
                                    ], limit=1)
                                    if cor_val:
                                        records[0]['product_id'] = cor_val.id
                                    else:
                                        records[0]['product_id'] = False

                                if records[0]['product_uom_id']:
                                    cor_val = self.env['uom.uom'].search([
                                        ('x_id_ext', '=', records[0]['product_uom_id'][0])
                                    ], limit=1)
                                    if cor_val:
                                        records[0]['product_uom_id'] = cor_val.id
                                    else:
                                        records[0]['product_uom_id'] = False

                                if records[0]['tax_ids']:
                                    for i in range(len(records[0]['tax_ids'])):
                                        cor_val = self.env['account.tax'].search([
                                            ('x_id_ext', '=', records[0]['tax_ids'][i])
                                        ], limit=1)
                                        if cor_val:
                                            records[0]['tax_ids'][i] = cor_val.id
                                        else:
                                            del records[0]['tax_ids'][i]
                                if records[0]['full_reconcile_id']:
                                    records[0]['old_ref_lettrage'] = records[0]['full_reconcile_id'][1]
                                    del records[0]['full_reconcile_id']

                                # print("UPDATED ==> ", records[0])
                                list_move_lines.append(records[0])

                            # print("MOVE LINES ==> ", list_move_lines)
                            # print("========================")
                            rec['line_ids'] = [(0, 0, line) for line in list_move_lines]

                            pprint(rec)
                        invoice_id = self.env[self.model_to_synchronize.model].create(rec)

                    else:
                        _logger.info("========= INVOICE LINE (Facture)============")
                        del rec['line_ids']
                        invoice_id = self.env[self.model_to_synchronize.model].create(rec)

                        records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                 'account.move.line', 'search_read',
                                                 [[['move_id', '=', int(invoice_id.x_id_ext)],
                                                   ['exclude_from_invoice_tab', '=', False],
                                                   ['display_type', '=', False]
                                                   ]],
                                                 {'fields': ['name', 'product_id', 'account_id', 'quantity',
                                                             'price_unit', 'discount', 'tax_ids', 'product_uom_id',
                                                             'display_type']})

                        _logger.info("========= INVOICE LINE DICT (FACTURE) ============")
                        _logger.info(records)

                        plan_comptable_a_lettre = mod.execute_kw(self.db_name, uid, self.pwd,
                                                                 'account.account', 'search_read',
                                                                 [[
                                                                     ['reconcile', '=', True]
                                                                 ]],
                                                                 {'fields': ['id', 'name']})
                        # print(plan_comptable_a_lettre)
                        code_comptes = []
                        if plan_comptable_a_lettre:
                            for p in plan_comptable_a_lettre:
                                code_comptes.append(p['id'])

                        # print(code_comptes)

                        ref_lettrage = ''
                        if code_comptes:
                            for cc in code_comptes:

                                acc = mod.execute_kw(self.db_name, uid, self.pwd,
                                                     'account.move.line', 'search_read',
                                                     [[['move_id', '=', int(invoice_id.x_id_ext)],
                                                       ['display_type', '=', False],
                                                       ['account_id', '=', cc]

                                                       ]],
                                                     {'fields': ['full_reconcile_id']})
                                # print(acc)
                                for line_f in acc:
                                    if line_f['full_reconcile_id']:
                                        if ref_lettrage == '' or ref_lettrage == line_f['full_reconcile_id'][1]:
                                            ref_lettrage = line_f['full_reconcile_id'][1]
                                        else:
                                            ref_lettrage = 'P'

                        # print("REF =>", ref_lettrage)

                        # print("TTTTT=> ", records)
                        for rec in records:
                            # pprint(rec)
                            # print(rec['account_id'])
                            rec['display_type'] = 'product'
                            rec['x_id_ext'] = rec['id']
                            del rec['id']
                            if rec['account_id']:
                                cor_val = self.env['account.account'].search([
                                    ('x_id_ext', '=', rec['account_id'][0])
                                ], limit=1)
                                if cor_val:
                                    rec['account_id'] = cor_val.id
                                else:
                                    rec['account_id'] = False

                            if rec['product_id']:
                                cor_val = self.env['product.product'].search([
                                    ('x_id_ext', '=', rec['product_id'][0])
                                ], limit=1)
                                if cor_val:
                                    rec['product_id'] = cor_val.id
                                else:
                                    rec['product_id'] = False

                            if rec['product_uom_id']:
                                cor_val = self.env['uom.uom'].search([
                                    ('x_id_ext', '=', rec['product_uom_id'][0])
                                ], limit=1)
                                if cor_val:
                                    rec['product_uom_id'] = cor_val.id
                                else:
                                    rec['product_uom_id'] = False

                            if rec['tax_ids']:
                                for i in range(len(rec['tax_ids'])):
                                    cor_val = self.env['account.tax'].search([
                                        ('x_id_ext', '=', rec['tax_ids'][i])
                                    ], limit=1)
                                    if cor_val:
                                        rec['tax_ids'][i] = cor_val.id
                                    else:
                                        del rec['tax_ids'][i]

                            rec['move_id'] = invoice_id.id
                            # rec['old_ref_lettrage'] = ref_lettrage
                            # print("=======================")
                            # pprint(rec)
                            # print("=======================")
                            # pprint(rec)
                            self.env['account.move.line'].create(rec)
                            invoice_id.write({'old_ref_lettrage': ref_lettrage})

            elif self.synch_operation == "update":
                records = self.env[self.model_to_synchronize.model].search(condition)

                for rec in records:

                    records_equiv = mod.execute_kw(self.db_name, uid, self.pwd,
                                                   self.model_to_synchronize_equiv, 'search_read',
                                                   [[[self.synchronization_key.name, '=',
                                                      rec[self.synchronization_key.name]]]],
                                                   {'fields': self.fields_to_synchronize.mapped("name"), 'limit': 1})

                    for field in self.fields_to_synchronize.mapped("name"):
                        rec[field] = records_equiv[0][field]
        except Exception as e:
            # print(e)
            self.message_post(
                body="%s" % e)

    def adapt_fields(self, model, field, value):
        search = self.check_if_field_exist(model, field)
        if model.model == 'account.move':
            if field == 'type':
                search = self.check_if_field_exist(model, 'move_type')

        if not search or field in ["create_uid", "create_date", "write_date", "write_uid", "id"]:
            if not search:
                self.message_post(
                    body="Le champs %s n'existe pas sur la table %s" % (field, self.model_to_synchronize.model))
            return False
        else:
            if search.ttype == "many2one":
                field_model = search.relation
                field_model_id = self.env['ir.model'].search([
                    ("model", "=", field_model)
                ]).id
                id_ext = self.env["ir.model.fields"].search([
                    ("model_id", "=", field_model_id),
                    ("name", "=", "x_id_ext")
                ])
                if not id_ext:
                    if value:
                        xml_id = self.has_xml_id(field_model, value[0])
                        self.env["ir.model.fields"].create({
                            "name": "x_id_ext",
                            "model_id": field_model_id,
                            "field_description": "ID Externe RPC",
                            "ttype": "char"
                        })
                        self.get_data_param(field_model, value[0])
                    return
                else:
                    if value:
                        correct_val = self.env[field_model].search([
                            ('x_id_ext', '=', value[0])
                        ], limit=1).id
                        # print(field)
                        # print(correct_val)
                    else:
                        # print("AAAAAAA")
                        correct_val = False

                    return {
                        field: correct_val
                    }

            elif search.ttype in ["many2many"]:
                return {
                    field: False
                }
            else:
                return {
                    field: value
                }

    def check_if_field_exist(self, model, field):
        search = self.env["ir.model.fields"].search([
            ("model_id", "=", model.id),
            ("name", "=", field)
        ])
        return search

    def get_data_param(self, model, value):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
        records = mod.execute_kw(self.db_name, uid, self.pwd, model, 'search_read', [[['id', '=', value]]])
        return records

    def has_xml_id(self, model, value):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
        records = mod.execute_kw(self.db_name, uid, self.pwd, 'ir.model.data', 'search_read',
                                 [[('res_id', '=', value), ('model', '=', model)]], {'fields': ['module', 'name']})
        # pprint(records)

        return records

    def check_ir_data(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        model_id = self.env['ir.model'].search([
            ("model", "=", "ir.model.data")
        ])
        # print(model_id)

        search = self.check_if_field_exist(model_id, "x_id_ext")
        # print(search)

        if not search:
            self.env["ir.model.fields"].create({
                "name": "x_id_ext",
                "model_id": model_id.id,
                "field_description": "ID Externe RPC",
                "ttype": "char"
            })

        models_list = ['res.currency', 'account.tax', 'account.payment.term', 'account.account']
        for model in models_list:
            model_id = self.env['ir.model'].search([
                ("model", "=", model)
            ])
            # print(model_id)

            search = self.check_if_field_exist(model_id, "x_id_ext")
            # print(search)

            if not search:
                self.env["ir.model.fields"].create({
                    "name": "x_id_ext",
                    "model_id": model_id.id,
                    "field_description": "ID Externe RPC",
                    "ttype": "char"
                })
            records_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                         'ir.model.data', 'search_read',
                                         [[['model', '=', model]]],
                                         {'fields': ['display_name', 'res_id']})

            records_v16 = self.env['ir.model.data'].search([
                ("model", "=", model)

            ])
            #
            for r_v16 in records_v16:
                for r_v13 in records_v13:
                    if r_v13['display_name'] == r_v16['display_name']:
                        aid = self.env[model].search([
                            ('id', '=', r_v16.res_id)
                        ])
                        aid.x_id_ext = r_v13['res_id']
                        r_v16.x_id_ext = r_v13['res_id']
        self.sync_uom()

    def sync_ref(self):
        # -------------------- RES PARTNER ---------------------
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'res.partner', 'search_read',
                                      [[]],
                                      {'fields': ['name']})
        # print("--------- V13 ------------")
        pprint(res_part_v13)

        res_part_v16 = self.env['res.partner'].search([])
        # print("--------- V16 ------------")

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.name == r_13['name']:
                    r_16.x_id_ext = r_13['id']
                    # print("V16=> ", r_16.x_id_ext)

        self.check_ir_data()

    def sync_article(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'product.product', 'search_read',
                                      [[]],
                                      {'fields': ['name']})
        # print("--------- V13 ------------")
        # pprint(res_part_v13)

        res_part_v16 = self.env['product.product'].search([])
        # print("--------- V16 ------------")

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.name == r_13['name']:
                    r_16.x_id_ext = r_13['id']
                    # print(r_16.name)

    def sync_taxes(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'account.tax', 'search_read',
                                      [[]],
                                      {'fields': ['name']})
        # print("--------- V13 ------------")
        # pprint(res_part_v13)

        res_part_v16 = self.env['account.tax'].search([])
        # print("--------- V16 ------------")

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.name == r_13['name']:
                    r_16.x_id_ext = r_13['id']
                    # print(r_16.name)

    def sync_fiscale(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'account.fiscal.position', 'search_read',
                                      [[]],
                                      {'fields': ['name']})
        # print("--------- V13 ------------")

        res_part_v16 = self.env['account.fiscal.position'].search([])
        # print("--------- V16 ------------")

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.name == r_13['name']:
                    r_16.x_id_ext = r_13['id']
                    # print(r_16.name)

    def sync_compte_bnk(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'res.partner.bank', 'search_read',
                                      [[]],
                                      {'fields': ['acc_number']})
        # print("--------- V13 ------------")

        res_part_v16 = self.env['res.partner.bank'].search([])
        # print("--------- V16 ------------")

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.acc_number == r_13['acc_number']:
                    r_16.x_id_ext = r_13['id']
                    # print(r_16.acc_number)

    def sync_journaux(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'account.journal', 'search_read',
                                      [[]],
                                      {'fields': ['name']})
        # print("--------- V13 ------------")

        res_part_v16 = self.env['account.journal'].search([])

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.name == r_13['name']:
                    r_16.x_id_ext = r_13['id']

    def sync_plan_comptable(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'account.account', 'search_read',
                                      [[]],
                                      {'fields': ['code']})
        # print("--------- V13 ------------")

        res_part_v16 = self.env['account.account'].search([])

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.code == r_13['code']:
                    r_16.x_id_ext = r_13['id']

    def sync_currencies(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_part_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                      'res.currency', 'search_read',
                                      [[]],
                                      {'fields': ['name']})
        # print("--------- V13 ------------")

        res_part_v16 = self.env['res.currency'].search([])

        for r_16 in res_part_v16:
            for r_13 in res_part_v13:
                if r_16.name == r_13['name']:
                    r_16.x_id_ext = r_13['id']

    def sync_uom(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        model_id = self.env['ir.model'].search([
            ("model", "=", 'uom.uom')
        ])
        # print(model_id)

        search = self.check_if_field_exist(model_id, "x_id_ext")
        # print(search)

        if not search:
            self.env["ir.model.fields"].create({
                "name": "x_id_ext",
                "model_id": model_id.id,
                "field_description": "ID Externe RPC",
                "ttype": "char"
            })
        records_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                     'ir.model.data', 'search_read',
                                     [[['model', '=', 'uom.uom']]],
                                     {'fields': ['complete_name', 'res_id']})

        records_v16 = self.env['ir.model.data'].search([
            ("model", "=", 'uom.uom')

        ])
        #
        for r_v16 in records_v16:
            for r_v13 in records_v13:
                if r_v13['complete_name'] == r_v16['complete_name']:
                    a = self.env['uom.uom'].search([
                        ('id', '=', r_v16.res_id)
                    ])
                    a.x_id_ext = r_v13['res_id']
                    r_v16.x_id_ext = r_v13['res_id']

    def sync_taux_change(self):
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})

        res_currency_rate_v13 = mod.execute_kw(self.db_name, uid, self.pwd,
                                               'res.currency.rate', 'search_read',
                                               [[]],
                                               {'fields': ['name', 'currency_id', 'rate']})

        # records_v16 = self.env['ir.model.data'].search([
        #     ("model", "=", 'res.currency.rate'),
        #     ()
        #
        # ])
        for rec in res_currency_rate_v13:
            if rec['currency_id']:
                currency_id = self.env['res.currency'].search([
                    ('x_id_ext', '=', rec['currency_id'][0])
                ])
                if currency_id:
                    curr_rate = self.env['res.currency.rate'].create({

                        "name": rec['name'],
                        "currency_id": currency_id.id,
                        "company_rate": rec['rate']

                    })
        # print(res_currency_rate_v13)
