# -*- coding: utf-8 -*-

import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class DbBackup(models.Model):
    _inherit = 'db.backup'

    @api.model
    def action_backup_all(self):
        """Run all scheduled backups."""
        return self.search([]).action_backup_queue()

    def action_backup_queue(self):
        self.with_delay().action_backup()
