# -*- coding: utf-8 -*-
import ftplib
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

try:
    import pysftp
except ImportError:
    _logger.debug('Cannot import pysftp')


class Models(models.Model):
    _name = 'ftp.connexion.test'
    _description = 'Test connexion FTP/FTPS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "host"

    host = fields.Char()
    user = fields.Char()
    port = fields.Integer()
    pwd = fields.Char()
    protocol = fields.Selection(
        [
            ("ftp", "FTP"),
            ("ftps", "FTPS"),
        ],
        default="ftp",
    )

    def test_connexion(self):
        if self.protocol == 'ftps':
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None

            try:

                pysftp.Connection(
                    host=self.host,
                    username=self.user,
                    password=self.pwd,
                    port=self.port,
                    cnopts=cnopts,

                )
                self.message_post(
                    body="Connection Test Successful!")

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Connection Test Successful!",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            except Exception as ee:
                self.message_post(
                    body="Connection Test Failed!")
                _logger.info("Connection Test Failed!:", exc_info=True)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Connection Test Failed!",
                        'type': 'danger',
                        'sticky': False,
                    }
                }

        elif self.protocol == 'ftp':
            try:
                server = ftplib.FTP(timeout=300)
                server.connect(self.host, self.port)
                server.login(self.user, self.pwd)
                self.message_post(
                    body="Connection Test Successful!")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Connection Test Successful!",
                        'type': 'success',
                        'sticky': False,
                    }
                }

            except Exception as e:
                self.message_post(
                    body="Connection Test Failed!")
                _logger.info("Connection Test Failed!:", exc_info=True)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Connection Test Failed!",
                        'type': 'danger',
                        'sticky': False,
                    }
                }
