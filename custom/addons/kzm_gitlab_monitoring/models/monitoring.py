from datetime import datetime
from odoo import fields, models
import paramiko
import OpenSSL
import ssl
from fabric2 import Connection

"""
    Monitoring model class for postgresql server
"""


class Monitoring(models.Model):
    """
        Monitoring model

    Args:
        models (models.Model): odoo orm model

    """
    _inherit = "project.database"
    _description = "Monitoring Postgresql Server"

    ssl_expiration_date = fields.Date('SSL Expiration Date')
    disk_usage = fields.Char('Disk Usage')
    sql_ip = fields.Char('Server IP')

    def synch_server(self, _hostname: str, _private_key: str, _username: str, _port: int) -> str:
        """
            get disk usage server

        Args:
            _hostname (str): server hostname
            _private_key (str): ssh private key
            _username (str): ssh username
            _password (str): ssh password
            _port (int): ssh exposed port

        Returns:
            str: disk usage in GB
        """
        with Connection(
                _hostname,
                _username,
                connect_kwargs=dict(
                    key_filename=[_private_key,
                                  ],
                ),
        ) as conn:
            disk_usage = conn.sudo("df -hP / | awk 'NR==2 {print $4}'")
            config_file = conn.sudo("cat /etc/odoo-server.conf")
            start = config_file.find("db_host")
            end = config_file[start:].find("\n")
            server_ip = config_file[start:start+end].split('=')[1].strip()
        return (disk_usage, server_ip)

    def get_ssl_cert_expiration_date(self, _domain: str) -> datetime.date:
        """
            get the ssl certification expiration date

        Args:
            _domain (str): domain

        Returns:
            datetime.date: expiration date
        """
        cert = ssl.get_server_certificate((_domain, 443))
        x509 = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cert)
        bytes = x509.get_notAfter()
        timestamp = bytes.decode('utf-8')
        return datetime.strptime(timestamp, '%Y%m%d%H%M%S%z').date().isoformat()

    def monitor_synch(self):
        """
            monitoring synchronization 
        """
        hostname = self.link
        username = "ubuntu"
        private_key = "/opt/id_rsa"
        port = 22
        try:
            disk_usage, server_ip = self.synch_server(hostname, private_key, username, port)
            self.write({'disk_usage': disk_usage})
            self.write({'sql_ip': server_ip})
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': "SSH Connection Failed",
                            'type': 'danger',
                            'sticky': False,
                        }
            }
        try:
            self.write(
                {'ssl_expiration_date': self.get_ssl_cert_expiration_date(hostname)})
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': "Encountring Error while getting ssl Certification Expiration Date",
                            'type': 'danger',
                            'sticky': False,
                        }

            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': "synchronized Successfully!",
                'type': 'success',
                'sticky': False,
            }
        }
