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
    
    

    def monitor_synch(self):
        hostname = self.ip
        username = "sshuser"
        password = "password"

        try:
            ssh = paramiko.SSHClient()
            k = paramiko.RSAKey.from_private_key_file(
                "/home/mmoumni/.ssh/id_rsa")
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname="localhost", username="sshuser",
                        password="password", port=2222, pkey=k, disabled_algorithms=dict(pubkeys=["rsa-sha2-512", "rsa-sha2-256"]))
            command = "df -hP / | awk 'NR==2 {print $4}'"
            stdin, stdout, stderr = ssh.exec_command(command)
            diskUsage:str = stdout.read().decode()
            self.write({'disk_usage': diskUsage})
            ssh.close()
            cert=ssl.get_server_certificate(('www.mmoumni.me', 443))
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            bytes=x509.get_notAfter()
            timestamp = bytes.decode('utf-8')
            self.write({'ssl_expiration_date': datetime.strptime(timestamp, '%Y%m%d%H%M%S%z').date().isoformat()})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "SSH Connected Successfully!",
                    'type': 'success',
                    'sticky': False,
                }
            }
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
