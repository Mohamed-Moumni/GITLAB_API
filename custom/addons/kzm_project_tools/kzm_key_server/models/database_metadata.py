# -*- coding: utf-8 -*-
import xmlrpc.client
from fabric2 import Connection

from odoo import models, fields, api, _


class DatabaseMetaData(models.Model):
    _name = 'database.metadata'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Database MetaData'

    name = fields.Char(required=True)
    size = fields.Char()
    project_database_id = fields.Many2one('project.database')
    link = fields.Char(related='project_database_id.link')
    protocole = fields.Selection(related='project_database_id.protocole')
    db_creation_date = fields.Datetime()
    is_backup_active = fields.Boolean()
    nbr_users = fields.Integer()
    users_ids = fields.One2many('db.res.users', 'database_metadata_id')
    installed_module_ids = fields.Many2many('ir.module.module')
    odoo_version = fields.Char()
    employee_ids = fields.One2many('client.hr.employee', 'database_metadata_id')
    c_user_ids = fields.One2many('client.res.users', 'database_metadata_id')
    user = fields.Char()
    password = fields.Char()
    installed_modules_ids = fields.One2many('installed.modules', 'database_metadata_id')

    def synch_data(self):
        view_id = self.env.ref('kzm_key_server.synch_data_wizard_view_form').id
        create_wizard = self.env['synch.data.wizard'].create(
            {'link': self.link, 'protocole': self.protocole, 'db_name': self.name,
             'database_metadata_id': self.id, 'pwd': self.password, 'login': self.user})
        try:
            val = create_wizard.synch_data()
            print(val)
            if val['params']['type'] == 'danger':
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Sync Data'),
                    'view_mode': 'form',
                    'res_model': 'synch.data.wizard',
                    'target': 'new',
                    # 'res_id': new_wizard.id,
                    'views': [[view_id, 'form']],
                    'context': {'default_link': self.link, 'default_protocole': self.protocole,
                                'default_db_name': self.name,
                                'default_database_metadata_id': self.id}
                }
        except Exception as e:
            return e

    def synch_path(self):

        if self.protocole == 'https':
            url = "https://%s" % self.link
        else:
            url = "http://%s" % self.link

        try:
            mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            # uid = mod_init.authenticate(self.db_name, self.login, self.pwd, {})
            uid = mod_init.authenticate(self.name, self.user, self.password, {})

            if uid:

                if self.installed_modules_ids:
                    # print(self.installed_modules_ids)

                    # installed_modules = self.env['installed.modules']
                    for rec in self.installed_modules_ids:
                        with Connection(
                                self.link,
                                user="ubuntu",
                                connect_kwargs=dict(
                                    key_filename=["/opt/id_rsa",
                                                  ]
                                )
                        ) as conn:
                            a = conn.sudo("find /opt/odoo -type d -name '%s'" % (rec.name), user='root')
                            files = str(a).splitlines()
                            path_list = files[2].split("/")
                            path = '/'.join(path_list[:-1])
                            # print('PATH ==>', path)
                            rec.path = path
                            rec.write({"path": path})

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        'params': {
                            'message': "Les données ont été synchronisées avec succès!",
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': "Veuillez synchroniser la liste des Applications !",
                            'type': 'danger',
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

    def action_open_database_metadata_form(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('kzm_key_server.action_database_metadata')
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('kzm_key_server.view_database_meatadata').id,
            'views': [(self.env.ref('kzm_key_server.view_database_meatadata').id, 'form')],
            'res_id': self.id,
        })
        return action
