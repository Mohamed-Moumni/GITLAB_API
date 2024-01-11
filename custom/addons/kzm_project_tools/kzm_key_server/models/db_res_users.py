# -*- coding: utf-8 -*-
import random
import string

from odoo import models, fields, api, _
import xmlrpc.client

from odoo.exceptions import ValidationError


class DbResUsers(models.Model):
    _inherit = "db.res.users"

    database_metadata_id = fields.Many2one('database.metadata')
    user_id_ext = fields.Integer()
    client_employee_id = fields.Many2one('client.hr.employee', store=True)
    # client_user_id = fields.Many2one('client.res.users')
    client_res_user_id = fields.Many2one('client.res.users')
    synched_with_client = fields.Boolean(string="Synched with client")

    def action_create(self):
        if self.database_metadata_id.protocole == 'https':
            url = "https://%s" % self.database_metadata_id.link
        else:
            url = "http://%s" % self.database_metadata_id.link

        # if self.user_id_ext == 0:
        #     raise ValidationError(
        #         _("Veuillez saisir l'ID de l'utilisateur! ")
        #     )

        try:
            mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            uid = mod_init.authenticate(self.database_metadata_id.name,
                                        self.database_metadata_id.user,
                                        self.database_metadata_id.password, {})
            # print(uid)
            # print(self.user_id_ext)
            kzm_key_client_installed = mod.execute_kw(self.database_metadata_id.name, uid,
                                                      self.database_metadata_id.password,
                                                      'ir.module.module', 'search_read',
                                                      [[['name', '=', 'kzm_key_client']]],
                                                      {'fields': ['name']})
            if kzm_key_client_installed:

                accessible_modules_list_ids = []
                if self.accessible_modules_ids:
                    for module_id in self.accessible_modules_ids:
                        rec_module = mod.execute_kw(self.database_metadata_id.name, uid, self.database_metadata_id.password,
                                                    'accessible.modules', 'search_read',
                                                    [[['id_ext', '=', module_id.id_ext]]],
                                                    {'fields': ['id_ext'], 'limit': 1})

                        accessible_modules_list_ids.append(rec_module[0]['id'])
                    print(accessible_modules_list_ids)

                val = mod.execute_kw(self.database_metadata_id.name, uid,
                                     self.database_metadata_id.password, 'db.res.users', 'create',
                                     [{
                                         'employee_ids': self.client_employee_id.id_ext,
                                         'res_user_id': self.client_res_user_id.id_ext,
                                         'key_licence': self.key_licence,
                                         'used': self.used,
                                         'is_active': self.is_active,
                                         'activation_date': self.activation_date,
                                         'expiration_date': self.expiration_date,
                                         'is_mobile': self.is_mobile,
                                         'modules_accessible': self.modules_accessible,
                                         'accessible_modules_ids': accessible_modules_list_ids,
                                     }]
                                     )
                self.id_ext = val
                self.synched_with_client = True
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                    'params': {
                        'message': "L'enregistrement a été créé avec succès!",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Le module kzm_key_client n'est pas installé sur la base du client!",
                        'type': 'danger',
                        'sticky': False,
                    }
                }

        except Exception as ee:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': ee,
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def action_maj(self):
        if self.database_metadata_id.protocole == 'https':
            url = "https://%s" % self.database_metadata_id.link
        else:
            url = "http://%s" % self.database_metadata_id.link
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = mod_init.authenticate(self.database_metadata_id.name,
                                    self.database_metadata_id.user,
                                    self.database_metadata_id.password, {})

        if self.id_ext:
            try:

                accessible_modules_list_ids = []
                if self.accessible_modules_ids:
                    for module_id in self.accessible_modules_ids:
                        rec_module = mod.execute_kw(self.database_metadata_id.name, uid,
                                                    self.database_metadata_id.password,
                                                    'accessible.modules', 'search_read',
                                                    [[['id_ext', '=', module_id.id_ext]]],
                                                    {'fields': ['id_ext'], 'limit': 1})

                        accessible_modules_list_ids.append(rec_module[0]['id'])
                    print(accessible_modules_list_ids)

                mod.execute_kw(self.database_metadata_id.name, uid,
                               self.database_metadata_id.password, 'db.res.users', 'write',
                               [self.id_ext,
                                {'key_licence': self.key_licence, 'used': self.used, 'is_active': self.is_active,
                                 'activation_date': self.activation_date, 'expiration_date': self.expiration_date,
                                 'modules_accessible': self.modules_accessible,
                                 'accessible_modules_ids': accessible_modules_list_ids,
                                 'is_mobile': self.is_mobile}])

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "L'enregistrement a été mis à jour avec succès!",
                        'type': 'success',
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

    def action_delete(self):
        if self.database_metadata_id.protocole == 'https':
            url = "https://%s" % self.database_metadata_id.link
        else:
            url = "http://%s" % self.database_metadata_id.link
        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = mod_init.authenticate(self.database_metadata_id.name,
                                    self.database_metadata_id.user,
                                    self.database_metadata_id.password, {})
        if self.id_ext:
            try:
                mod.execute_kw(self.database_metadata_id.name, uid,
                               self.database_metadata_id.password, 'db.res.users', 'unlink',
                               [self.id_ext])

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "L'enregistrement a été supprimé avec succès!",
                        'type': 'success',
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

    def unlink(self):
        for r in self:
            r.action_delete()
        return super().unlink()

    def generate_key(self):
        x = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        return x

    @api.model
    def create(self, vals):
        print(vals)
        if 'key_licence' not in vals:
            vals['key_licence'] = self.generate_key()
        res = super(DbResUsers, self).create(vals)

        return res

    @api.constrains("client_employee_id", "key_licence")
    def _check_employee_key_unique(self):
        check = self.env['db.res.users'].search([
            ('key_licence', '=', self.key_licence),
            ('client_employee_id', '!=', self.client_employee_id.id),
            ('database_metadata_id', '=', self.database_metadata_id.id),

        ])
        print(check)
        if check:
            raise ValidationError(
                _("On ne peut pas avoir deux lignes différentes avec la même clé et deux employés différents!")
            )
