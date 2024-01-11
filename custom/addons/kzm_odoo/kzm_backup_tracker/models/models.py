# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, timedelta, date

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import exceptions as GC_exceptions
from google.cloud import storage
from odoo import _, exceptions, fields, models

_logger = logging.getLogger(__name__)


class GcloudBackupTracker(models.Model):
    _name = 'kzm.backup.tracker'
    _description = "Backup Tracker"

    def _compute_nb_lines(self):
        for r in self:
            r.nbr_of_lines = len(r.gcloud_lines.ids)

    GOOGLE_APPLICATION_CREDENTIALS = fields.Char("GOOGLE STORAGE PATH", required=True)
    name = fields.Char(string="Bucket ID",
                       help="https://console.cloud.google.com/storage/browser/["
                            "bucket-id]/",
                       required=True)
    start_date = fields.Datetime("date_debut")
    end_date = fields.Datetime("date_fin")
    backup_name = fields.Char("Backup name")
    count_backups = fields.Integer("count backups")
    gcloud_lines = fields.One2many('kzm.backup.tracker.lines', 'gcloud_backup_id',
                                   string="GCloud Lines")
    nbr_of_lines = fields.Integer("Nb lignes", compute=_compute_nb_lines)

    # Tester la connexion vers Google Cloud
    logger = logging.getLogger(__name__)

    def test_connection(self):
        # """Prints out a bucket's metadata."""
        try:
            # """Prints out a bucket's metadata."""
            if self.GOOGLE_APPLICATION_CREDENTIALS:
                os.environ[
                    "GOOGLE_APPLICATION_CREDENTIALS"] = \
                    self.GOOGLE_APPLICATION_CREDENTIALS
            else:
                _logger.info("Error: GOOGLE_APPLICATION_CREDENTIALS not specified")
                # print("Error: GOOGLE_APPLICATION_CREDENTIALS not specified")
            client = storage.Client()
            bucket = client.get_bucket(self.name)
            if bucket:
                raise exceptions.Warning(_("Connection Test Succeeded!"))
        except (GC_exceptions.NotFound,
                DefaultCredentialsError) as e:
            raise exceptions.Warning(_("Connection Test Failed!\n " + str(e)))

    # Etablir la connexion vers Google Cloud
    def gcloud_connection(self):
        tracker_ids = self.env['kzm.backup.tracker'].search([])
        # print(tracker_ids)
        for r in tracker_ids:
            try:
                # """Prints out a bucket's metadata."""
                if r.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ[
                        "GOOGLE_APPLICATION_CREDENTIALS"] = \
                        r.GOOGLE_APPLICATION_CREDENTIALS
                else:
                    print("Error: GOOGLE_APPLICATION_CREDENTIALS not specified")
                client = storage.Client()
                bucket = client.get_bucket(r.name)
                # print(r.name, bucket, bucket.name)
                for kbtl in r.gcloud_lines:
                    blobs = bucket.list_blobs(prefix=kbtl.backup_path, delimiter='')
                    r.create_datas(blobs, kbtl)
                # raise exceptions.Warning(_("Connection Test Succeeded!"))
            except GC_exceptions.NotFound:
                msg = "Error: Sorry, that bucket (%s) does not exist!" % r.name
                _logger.info("Connection Test Failed!:" + msg, exc_info=True)
                raise exceptions.Warning(_("Connection Test Failed!\n " + msg))

    # Création des records
    def create_datas(self, blobs, kzm_backup_tracker_lines):
        successful = self.browse()
        for kbtl in kzm_backup_tracker_lines:
            liste = []
            on_date = fields.Datetime.to_string(datetime.today().replace(hour=12))
            for blob in blobs:
                # from pprint import pprint
                # pprint(blob)
                on_date = fields.Datetime.to_string(blob.updated.replace(hour=12))
                name = os.path.basename(blob.name)
                start_date = fields.Datetime.to_string(blob.updated.replace(hour=3))
                end_date = fields.Datetime.to_string(blob.updated.replace(hour=21))
                # blob.content_type == 'application/zip':
                # print(blob.updated.date())
                if True:
                    if blob.updated.date() == datetime.today().date():
                        record = self.env['kzm.backup.tracker.gantt'].search(
                            [('start_date', '<=', on_date),
                             ('end_date', '>=', on_date),
                             ('gcloud_backup_line', '=', kbtl.id)])
                        # print("recc", record, line)
                        if len(record) > 0:
                            # print("in")
                            record.unlink()
                        values = {
                            'name': name,
                            'start_date': start_date,
                            'end_date': end_date,
                            'backup_name': kbtl.backup_name,
                            'backup_path': kbtl.backup_path,
                            'days_to_keep': kbtl.days_to_keep,
                            'gcloud_backup_line': kbtl.id
                        }
                        liste.append(values)
            count = len(liste)
            for i in liste:
                if count > 1:
                    i['color'] = 3
                    self.env["kzm.backup.tracker.gantt"].create(i)
                elif count == 1:
                    i['color'] = 10
                    self.env["kzm.backup.tracker.gantt"].create(i)
            i = {}
            if count == 0:
                i['color'] = 9
                i['start_date'] = fields.Datetime.to_string(datetime.today().replace(hour=3))
                i['end_date'] = fields.Datetime.to_string(datetime.today().replace(hour=21))
                i['name'] = "Not Found"
                i['backup_name'] = kbtl.backup_name
                i['backup_path'] = kbtl.backup_path
                i['days_to_keep'] = kbtl.days_to_keep
                i['gcloud_backup_line'] = kbtl.id
                record = self.env["kzm.backup.tracker.gantt"].search(
                    [('start_date', '<=', on_date),
                     ('end_date', '>=', on_date),
                     ('name', '=', "Not Found"),
                     ('gcloud_backup_line', '=', kbtl.id)])
                if len(record) > 0:
                    record.unlink()
                # pprint(i)
                self.env["kzm.backup.tracker.gantt"].create(i)
        successful.cleanup(kzm_backup_tracker_lines)

    def cleanup(self, kzm_backup_tracker_lines):
        """Clean up old backups."""
        today = date.today()
        for kbtl in kzm_backup_tracker_lines:
            for rec in self.env['kzm.backup.tracker.gantt'].search([('gcloud_backup_line', '=', kbtl.id)]):
                oldest = today - timedelta(days=rec.days_to_keep)
                if rec.name and rec.start_date.date() == oldest:
                    rec.unlink()

    def action_see_lines(self):
        action = self.sudo().env.ref(
            'kzm_backup_tracker.kzm_backup_tracker_lines_action_window').read()[0]
        action['domain'] = [('gcloud_backup_id', '=', self.id)]
        action['context'] = dict(self.env.context, default_gcloud_backup_id=self.id,
                                 group_by=False)
        action['views'] = [
            (self.sudo().env.ref(
                'kzm_backup_tracker.kzm_backup_tracker_bucket_lines').id, 'tree'),
        ]
        return action


class GcloudBackupTrackerLines(models.Model):
    _name = 'kzm.backup.tracker.lines'
    _description = "Gcloud Tracker lines"
    _order = 'sequence'
    _rec_name = 'backup_path'

    GOOGLE_APPLICATION_CREDENTIALS = fields.Char("GOOGLE STORAGE PATH",
                                                 related="gcloud_backup_id.GOOGLE_APPLICATION_CREDENTIALS")
    name = fields.Char(string="Bucket ID",
                       help="https://console.cloud.google.com/storage/browser/["
                            "bucket-id]/",
                       related="gcloud_backup_id.name")
    backup_name = fields.Char(string="Backup name", required=True)
    backup_path = fields.Char(string="Backup path", required=True)
    gcloud_backup_id = fields.Many2one('kzm.backup.tracker', string="GCloud Backup Id")
    days_to_keep = fields.Integer(string="Days to keep", default=20, required=True)
    sequence = fields.Integer("Sequence", default=1)
    active = fields.Boolean(default=True)

    def refresh_bucket(self):
        for r in self:
            try:
                if r.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ[
                        "GOOGLE_APPLICATION_CREDENTIALS"] = \
                        r.GOOGLE_APPLICATION_CREDENTIALS
                else:
                    _logger.info("Error: GOOGLE_APPLICATION_CREDENTIALS not specified")
                    # print("Error: GOOGLE_APPLICATION_CREDENTIALS not specified")

                client = storage.Client()
                bucket = client.get_bucket(r.name)
                blobs = bucket.list_blobs(prefix=r.backup_path, delimiter='')

                r.gcloud_backup_id.create_datas(blobs, r)
            except GC_exceptions.NotFound:
                msg = "Error: Sorry, that bucket (%s) does not exist!" % r.name
                _logger.info("Connection Test Failed!:" + msg, exc_info=True)
                raise exceptions.Warning(_("Connection Test Failed!\n " + msg))


class BackupTrackerGantt(models.Model):
    _name = 'kzm.backup.tracker.gantt'
    _description = "Backup Tracker gantt"

    start_date = fields.Datetime("Date debut")
    end_date = fields.Datetime("Date fin")
    backup_name = fields.Char("Bucket name")
    backup_path = fields.Char("Backup path")
    name = fields.Char("Backup Name")
    role_id = fields.Many2one('planning.role', string="Role id")

    color = fields.Integer("Color", default=0)
    state = fields.Char("State")
    days_to_keep = fields.Integer("Days to keep", default=20)
    gcloud_backup_line = fields.Many2one('kzm.backup.tracker.lines', string="GCloud "
                                                                            "Backup "
                                                                            "Line"
                                         )
    bucket_name = fields.Char("Bucket name old")  # to remove

    def get_link_to_dwnld(self):
        return {
            "type": "ir.actions.act_url",
            "url": "https://storage.cloud.google.com/kzm/%s/%s" % (self.backup_path, self.name),
        }

    def cron_recap_mail(self):
        date_min = datetime.today().date()
        date_max = date_min + timedelta(days=1)

        failed_records = self.env['kzm.backup.tracker.gantt'].search([
            ('color', '=', 9),
            ('start_date', '>=', date_min),
            ('end_date', '<', date_max)
        ])
        # print('start date', failed_records.start_date)
        # print('end date', failed_records.end_date)

        double_records = self.env['kzm.backup.tracker.gantt'].search([
            ('color', '=', 3),
            ('start_date', '>=', date_min),
            ('end_date', '<', date_max)
        ])

        # --------------------- SEND MAIL ---------------------

        backup_mail_group = self.env.ref('kzm_backup_tracker.group_manager')
        # print(backup_mail_group.users.mapped('login'))

        template = self.env.ref('kzm_backup_tracker.mail_template_recap_backup')

        email_values_ctx = {
            'partner_to': ','.join([str(partner.id) for partner in backup_mail_group.users.mapped('partner_id')]),
            'failed_records': failed_records,
            'double_records': double_records,
            'date': date_min.strftime('%d/%m/%Y')
        }
        if failed_records or double_records:
            template.with_context(email_values_ctx).send_mail(self.id)
