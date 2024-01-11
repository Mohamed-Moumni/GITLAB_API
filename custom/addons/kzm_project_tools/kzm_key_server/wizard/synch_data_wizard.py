# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import xmlrpc.client
from fabric2 import Connection
import logging

_logger = logging.getLogger(__name__)


class SynchDataWizard(models.TransientModel):
    _name = 'synch.data.wizard'

    login = fields.Char(required=1)
    pwd = fields.Char(required=1)
    link = fields.Char(string=_("Link"))
    protocole = fields.Char()
    db_name = fields.Char()
    installed_modules_ids = fields.One2many('installed.modules', 'database_metadata_id')
    database_metadata_id = fields.Many2one('database.metadata')

    def synch_data(self):
        if self.database_metadata_id.protocole == 'https':
            url = "https://%s" % self.link
        else:
            url = "http://%s" % self.link

        _logger.info("========= URL ============")
        _logger.info(url)

        try:
            mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            _logger.info("======> 1", mod_init)
            mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            _logger.info("======> 2", mod_init)
            # uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
            uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
            if uid:
                records = mod.execute_kw(self.db_name, uid, self.pwd,
                                         'ir.config_parameter', 'search_read',
                                         [[['key', '=', 'database.create_date']]],
                                         {'fields': ['value'], 'limit': 1})

                # print("database creation date:", records)
                db_creation_date = records[0]['value']
                # print("database creation date:", db_creation_date)
                meta_data = self.env['database.metadata'].search([
                    ('id', '=', self.database_metadata_id.id)
                ])

                kzm_key_client_installed = mod.execute_kw(self.db_name, uid, self.pwd,
                                                          'ir.module.module', 'search_read',
                                                          [[['name', '=', 'kzm_key_client']]],
                                                          {'fields': ['name']})

                # print('=========> KZM KEY CLEINT:', kzm_key_client_installed)

                db_backup_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                   'db.backup', 'search_read',
                                                   [[]],
                                                   {'fields': ['name', 'folder']})

                is_backup_active = False
                if db_backup_records:
                    is_backup_active = True

                # print("is_backup_active: ", is_backup_active)

                nb_user_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                 'res.users', 'search_read',
                                                 [[]],
                                                 {'fields': ['name', 'login', 'active', 'create_date']})

                users_number = len(nb_user_records)
                # print("Nb users: ", users_number)

                # ------------------

                meta_data.db_creation_date = db_creation_date
                meta_data.is_backup_active = is_backup_active
                meta_data.nbr_users = users_number

                # ----------------------------------
                clean_emlployees_rec = self.env['client.hr.employee'].search([
                    ('database_metadata_id', '=', meta_data.id)
                ])
                if clean_emlployees_rec:
                    clean_emlployees_rec.unlink()

                # ---------------------

                employees_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                   'hr.employee', 'search_read',
                                                   [[]],
                                                   {'fields': ['name']})

                employees = self.env['client.hr.employee']
                # print(employees_records)

                for rec_emp in employees_records:
                    employee_id = self.env['client.hr.employee'].create({
                        "name": rec_emp['name'],
                        "id_ext": rec_emp['id']
                    })
                    employees += employee_id

                meta_data.employee_ids = employees

                # --------------

                c_users = self.env['client.res.users']

                if kzm_key_client_installed:
                    client_user_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                         'res.users', 'search_read',
                                                         [[]],
                                                         {'fields': ['name', 'is_mobile_user']})
                    for rec_user in client_user_records:
                        c_user_id = self.env['client.res.users'].create({
                            "name": rec_user['name'],
                            "id_ext": rec_user['id'],
                            "is_mobile": rec_user['is_mobile_user'],
                            "database_metadata_id": meta_data.id
                        })
                        c_users += c_user_id

                    meta_data.c_user_ids = c_users
                else:
                    client_user_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                         'res.users', 'search_read',
                                                         [[]],
                                                         {'fields': ['name']})
                    for rec_user in client_user_records:
                        c_user_id = self.env['client.res.users'].create({
                            "name": rec_user['name'],
                            "id_ext": rec_user['id'],
                            # "is_mobile": rec_user['is_mobile_user'],
                            "database_metadata_id": meta_data.id
                        })
                        c_users += c_user_id

                    meta_data.c_user_ids = c_users

                data_to_clean = self.env['db.res.users'].search([
                    ('database_metadata_id', '=', meta_data.id)
                ])
                if data_to_clean:
                    data_to_clean.unlink()

                if kzm_key_client_installed:
                    user_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                  'db.res.users', 'search_read',
                                                  [[['employee_ids', '!=', False]]],
                                                  {'fields': ['employee_ids', 'is_active', 'key_licence',
                                                              'activation_date',
                                                              'expiration_date', 'used', 'modules_accessible',
                                                              'accessible_modules_ids',
                                                              'create_date', 'client_user_id']})
                    users = self.env['db.res.users']
                    # print("TTTTTTTTTTTT", user_records)

                    for rec_user in user_records:
                        employee_correct_val = self.env['client.hr.employee'].search([
                            ('id_ext', '=', rec_user['employee_ids'][0]),
                            ('database_metadata_id', '=', meta_data.id)
                        ], limit=1)
                        user_correct_val = self.env['client.res.users'].search([
                            ('id_ext', '=', rec_user['client_user_id']),
                            ('database_metadata_id', '=', meta_data.id)
                        ], limit=1)

                        accessible_modules_list_ids = []
                        if rec_user['accessible_modules_ids']:
                            for module_id in rec_user['accessible_modules_ids']:
                                rec_module = mod.execute_kw(self.db_name, uid, self.pwd,
                                                            'accessible.modules', 'search_read',
                                                            [[['id', '=', module_id]]],
                                                            {'fields': ['id_ext'], 'limit': 1})

                                correct_val = self.env['accessible.modules'].search([
                                    ('id_ext', '=', rec_module[0]['id_ext'])
                                ])
                                accessible_modules_list_ids.append(correct_val.id)

                        # print(accessible_modules_list_ids)

                        user_id = self.env['db.res.users'].sudo().create({
                            "name": rec_user['employee_ids'][1],
                            "client_employee_id": employee_correct_val.id,
                            "user_id_ext": rec_user['client_user_id'],
                            "client_res_user_id": user_correct_val.id,
                            "id_ext": rec_user['id'],
                            "is_active": rec_user['is_active'],
                            "key_licence": rec_user['key_licence'],
                            "activation_date": rec_user['activation_date'],
                            "expiration_date": rec_user['expiration_date'],
                            "used": rec_user['used'],
                            "create_date": rec_user['create_date'],
                            "modules_accessible": rec_user['modules_accessible'],
                            "accessible_modules_ids": accessible_modules_list_ids,
                            "synched_with_client": True

                        })
                        users += user_id
                    #
                    meta_data.users_ids = users

                installed_module_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                          'ir.module.module', 'search_read',
                                                          [[['state', '=', 'installed']]],
                                                          {'fields': ['name', 'dependencies_id', 'installed_version']})

                # print(installed_module_records)
                installed_modules = self.env['installed.modules']
                for rec in installed_module_records:
                    if rec['name']:
                        # print(rec['dependencies_id'])
                        dependency = ""
                        for dep in rec['dependencies_id']:
                            rec_dep = mod.execute_kw(self.db_name, uid, self.pwd,
                                                     'ir.module.module.dependency', 'search_read',
                                                     [[['id', '=', dep]]],
                                                     {'fields': ['name']})
                            # print("===> ", rec_dep)
                            dependency += '%s, ' % rec_dep[0]['name']

                        installed_module_id = self.env['installed.modules'].sudo().create({
                            "name": rec['name'],
                            "version": rec['installed_version'],
                            "dependencies": dependency

                        })
                        installed_modules += installed_module_id
                        # print(rec['dependencies_id'])

                meta_data.installed_modules_ids = installed_modules

                odoo_version_records = mod.execute_kw(self.db_name, uid, self.pwd,
                                                      'ir.module.module', 'search_read',
                                                      [[['name', '=', 'base']]],
                                                      {'fields': ['installed_version'], 'limit': 1})

                meta_data.odoo_version = odoo_version_records[0]['installed_version']
                self.database_metadata_id.user = "kadmin"
                self.database_metadata_id.password = self.pwd

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Données synchronisées avec succès !",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Identifiants de connexion incorrects ou service Odoo inaccessible!",
                        'type': 'danger',
                        'sticky': False,
                    }
                }

        except Exception as ee:
            print(ee)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': ee,
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def action_pwd_reset(self):
        # print("TTT")
        with Connection(
                self.link,
                user="ubuntu",
                connect_kwargs=dict(
                    key_filename=["/opt/id_rsa",
                                  ]
                )
        ) as conn:
            a = conn.sudo(
                'psql -U postgres -c "\c %s" -c "update res_users set login='"'"'%s'"'"' where id=2;" -c "update res_users set password='"'"'%s'"'"' where id=2;"' % (
                    self.db_name, "kadmin", self.pwd),
                user='postgres')

            self.database_metadata_id.user = "kadmin"
            self.database_metadata_id.password = self.pwd
