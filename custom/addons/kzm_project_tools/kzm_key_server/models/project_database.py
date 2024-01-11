# -*- coding: utf-8 -*-
import socket

from odoo import fields, models, api, _
import subprocess
import paramiko
from fabric2 import Connection
from telnetlib import Telnet
import time

from odoo.exceptions import ValidationError


class ProjectDatabase(models.Model):
    _inherit = 'project.database'
    _sql_constraints = [("link_uniq", "UNIQUE (link)", "Adresse IP/Url doit être unique!")]

    db_user = fields.Char()
    db_password = fields.Char()
    db_record_ids = fields.One2many('database.metadata', 'project_database_id', readonly=False)
    protocole = fields.Selection([
        ("http", "HTTP"),
        ("https", "HTTPS"),

    ],
        default="https", )

    config_file = fields.Text()

    def test_ping(self):
        # ping_test = subprocess.call("ping %s" % self.link)
        try:
            out = subprocess.check_output(['ping', '-c', '1', self.link])
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Ping Test Successful!",
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "L'instance n'est pas disponibe",
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def test_ssh(self):
        try:
            ssh = paramiko.SSHClient()
            # k = paramiko.RSAKey.from_private_key_file("/home/mac/.ssh/id_rsa")
            k = paramiko.RSAKey.from_private_key_file("/opt/id_rsa")
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.link, username="ubuntu", pkey=k)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "SSH Test Successful!",
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            print(e)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "SSH Test Failed!",
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def get_all_dbs(self):
        for old_db_rec in self.db_record_ids:
            old_db_rec.unlink()

        with Connection(
                self.link,
                user="ubuntu",
                connect_kwargs=dict(
                    key_filename=["/opt/id_rsa",
                                  ]
                )
        ) as conn:
            a = conn.sudo('psql -U postgres -c "\l+"', user='postgres')
            files = str(a).splitlines()
            list_db = files[5:-4]

            db_names = []

            for db in list_db:
                db_dict = {}
                db_without_space = db.strip()
                db_name = db_without_space.split('|')[0].strip()
                db_size = db_without_space.split('|')[6].strip()
                if db_name not in ['postgres', 'template0', 'template1', '']:
                    db_dict['name'] = db_name
                    db_dict['size'] = db_size
                    db_names.append(db_dict)

            # print(db_names)

            for rec in db_names:
                r = self.env['database.metadata'].create(rec)
                r.project_database_id = self.id

    def get_config_file(self):
        # print("testtststs")
        with Connection(
                self.link,
                user="ubuntu",
                connect_kwargs=dict(
                    key_filename=["/opt/id_rsa",
                                  ]
                )
        ) as conn:
            a = conn.sudo('cat /etc/odoo-server.conf')
            files = str(a).splitlines()
            # print(files[2:-1])
            conf_file = '\n'.join(files[2:-1])
            self.config_file = conf_file

    def test_odoo_service(self):
        try:
            with Connection(
                    self.link,
                    user="ubuntu",
                    connect_kwargs=dict(
                        key_filename=["/opt/id_rsa",
                                      ]
                    )
                    , connect_timeout=500
            ) as conn:
                a = conn.run('ps aux | grep odoo')

                files = str(a).splitlines()
                # print("===> ", files[2:-2])
                is_up = False
                for f in files[2:-2]:
                    sp = f.split(" ")
                    user = sp[0]
                    command = " ".join(sp[30:])
                    if user == "odoo" and command == "python3 /opt/odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf":
                        is_up = True
                        break
                # print(is_up)
                if is_up:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': "Odoo service is UP",
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': "Odoo service is Down",
                            'type': 'danger',
                            'sticky': False,
                        }

                    }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Veuillez vérifier la connexion SSH",
                    'type': 'danger',
                    'sticky': False,
                }

            }

    def start_odoo_service(self):
        a = self.test_odoo_service()
        print(a)
        if a['params']['type'] == "success":
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Le service Odoo est dèja lancé",
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            try:
                with Connection(
                        self.link,
                        user="ubuntu",
                        connect_kwargs=dict(
                            key_filename=["/opt/id_rsa",
                                          ]
                        )
                ) as conn:
                    a = conn.sudo('/etc/init.d/odoo-server start')
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': "Service Odoo a été lancé avec succès",
                            'type': 'success',
                            'sticky': False,
                        }
                    }
            except Exception as e:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Veuillez vérifier la connexion SSH",
                        'type': 'danger',
                        'sticky': False,
                    }
                }

    def stop_odoo_service(self):
        try:

            with Connection(
                    self.link,
                    user="ubuntu",
                    connect_kwargs=dict(
                        key_filename=["/opt/id_rsa",
                                      ]
                    )
            ) as conn:
                for i in range(4):
                    a = conn.sudo('/etc/init.d/odoo-server stop')
                    time.sleep(2)

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Service Odoo a été arreté avec succès",
                        'type': 'success',
                        'sticky': False,
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Veuillez vérifier la connexion SSH",
                    'type': 'danger',
                    'sticky': False,
                }
            }
