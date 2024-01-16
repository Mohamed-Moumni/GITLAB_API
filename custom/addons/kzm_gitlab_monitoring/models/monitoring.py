from datetime import datetime
from odoo import fields, models
from fabric2 import Connection
import OpenSSL
import ssl
import re
import configparser

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
    sql_server_id = fields.Many2one(
        'database.server', string='Sql Server')

    def synch_server(self, _hostname: str, _private_key: str, _username: str) -> str:
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
                user=_username,
                connect_kwargs=dict(
                    key_filename=[_private_key],
                )
        ) as conn:
            disk_usage = conn.sudo(
                "df -h / | awk 'NR==2 {print $3\" / \"$2\" ( \"$5\" )\"}'").stdout
            config_file = conn.sudo("cat /etc/odoo-server.conf").stdout
            configParser = configparser.ConfigParser()
            configParser.read_string(config_file)
            server_ip = configParser.get('options', 'db_host')
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
        try:
            disk_usage, server_ip = self.synch_server(
                hostname, private_key, username)
            self.write({'disk_usage': disk_usage})
            database_server_found = self.env['database.server'].search(
                [('ip', '=', server_ip)])

            if not database_server_found:
                database_server = self.env['database.server'].create({'ip': server_ip, 'name': self.env['ir.sequence'].next_by_code(
                    'kzm_gitlab_monitoring.sequence')})
                self.write({'sql_server_id': database_server.id})
            else:
                self.write({'sql_server_id': database_server_found.id})

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