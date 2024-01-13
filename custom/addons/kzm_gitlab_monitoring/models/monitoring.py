from datetime import datetime
from odoo import fields, models
import paramiko
import OpenSSL
import ssl

"""
    Monitoring model class for postgresql server
"""


class Monitoring(models.Model):
    _inherit = "project.database"
    _description = "Monitoring Postgresql Server"

    ssl_expiration_date = fields.Date('SSL Expiration Date')
    disk_usage = fields.Char('Disk Usage')
    ip = fields.Char('Postgresql server IP')

    database_server_id = fields.Many2one(
        'database.server', string='Database Server')

    def synch_disk_usage(self, _hostname: str, _private_key: str, _username: str, _password: str, _port: int) -> str:
        ssh = paramiko.SSHClient()
        private_key = paramiko.RSAKey.from_private_key_file(_private_key)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=_hostname, username=_username, password=_password,
                    port=_port, pkey=private_key, disabled_algorithms=dict(pubkeys=["rsa-sha2-512", "rsa-sha2-256"]))
        command: str = "df -hP / | awk 'NR==2 {print $4}'"
        stdin, stdout, stderr = ssh.exec_command(command)
        disk_usage: str = stdout.read().decode()
        ssh.close()
        return disk_usage

    def get_ssl_cert_expiration_date(self, _domain: str) -> datetime.date:
        cert = ssl.get_server_certificate((_domain, 443))
        x509 = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cert)
        bytes = x509.get_notAfter()
        timestamp = bytes.decode('utf-8')
        return datetime.strptime(timestamp, '%Y%m%d%H%M%S%z').date().isoformat()

    def monitor_synch(self):
        hostname = self.ip
        username = "sshuser"
        password = "password"
        private_key = "/home/mmoumni/.ssh/id_rsa"
        port = 2222
        try:
            self.write({'disk_usage': self.synch_disk_usage(
                hostname, private_key, username, password, port)})
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
                {'ssl_expiration_date': self.get_ssl_cert_expiration_date("www.mmoumni.me")})
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
