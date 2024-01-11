# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
from datetime import datetime, timedelta
from glob import iglob
import tempfile
from google.cloud import exceptions as GC_exceptions
from google.cloud import storage
from odoo import _, api, exceptions, fields, models
from odoo.service import db

_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')


class DbBackup(models.Model):
    _name = 'db.backup'
    _inherit = ['db.backup', 'mail.thread', 'mail.activity.mixin']

    method = fields.Selection(selection_add=[("gcloud", "Google cloud storage")], default="local",
                              help="Choose the storage method for this backup.", )
    GOOGLE_APPLICATION_CREDENTIALS = fields.Char("GOOGLE APPLICATION CREDENTIALS PATH")
    bucket_name = fields.Char(string="Bucket ID",
                              help="https://console.cloud.google.com/storage/browser"
                                   "/[bucket-id]/")

    @api.model
    def _get_db_name(self):
        folder = "%s/%s-PROD" % (self.env.cr.dbname, self.env.cr.dbname)
        datas = {
            'folder': folder,
            'days_to_keep': 10,
            'method': 'gcloud',
            'backup_format': 'zip',
            'GOOGLE_APPLICATION_CREDENTIALS': '/opt/gcloud/GCLOUD-STORAGE/KARIZMA-CLOUD-ca1aa0dd8fd1.json',
            'bucket_name': 'kzm'
        }
        id_created = self.env.ref('oca_auto_backup_extension.gcloud_backup_id', raise_if_not_found=False) or self.env[
            'db.backup'].search([('folder', '=', folder)])
        if id_created:
            id_created.write(datas)
        else:
            id_created = self.create(datas)

        try:
            id_created.action_gcloud_test_connection()
            id_created.message_post(body="Backup bien actif")
        except Exception as e:
            id_created.message_post(body=str(e))

    def sftp_connection(self):
        """Return a new SFTP connection with found parameters."""
        self.ensure_one()
        if self.method != 'gcloud':

            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            params = {
                "host": self.sftp_host,
                "username": self.sftp_user,
                "port": self.sftp_port,
                "cnopts": cnopts,
            }
            _logger.debug(
                "Trying to connect to sftp://%(username)s@%(host)s:%(port)d",
                extra=params)
            if self.sftp_private_key:
                params["private_key"] = self.sftp_private_key
                if self.sftp_password:
                    params["private_key_pass"] = self.sftp_password
            else:
                params["password"] = self.sftp_password

            return pysftp.Connection(**params)
        else:
            if self.GOOGLE_APPLICATION_CREDENTIALS:
                os.environ[
                    "GOOGLE_APPLICATION_CREDENTIALS"] = \
                    self.GOOGLE_APPLICATION_CREDENTIALS
            else:
                _logger.debug("Error: GOOGLE_APPLICATION_CREDENTIALS not specified")
            client = storage.Client()
            bucket = client.get_bucket(self.bucket_name)
            return bucket

    def action_backup(self):
        # """Run selected backups."""
        filename = self.filename(datetime.now())
        successful = self.browse()

        gcloud = self.filtered(lambda r: r.method == "gcloud")
        if gcloud:
            for rec in gcloud:
                with rec.backup_log():
                    if rec.backup_format == 'zip':
                        cached = db.dump_db(
                            self.env.cr.dbname,
                            None,
                            backup_format=rec.backup_format
                        )
                        bucket = rec.sftp_connection()
                        if bucket:
                            path_to = os.path.join(rec.folder, filename)
                            blob = bucket.blob(path_to)
                            blob.upload_from_file(cached)
                    else:
                        with tempfile.TemporaryFile(mode='w+b') as t:
                            db.dump_db(
                                self.env.cr.dbname,
                                t,
                                backup_format=rec.backup_format
                            )
                            t.seek(0)
                            bucket = rec.sftp_connection()
                            if bucket:
                                path_to = os.path.join(rec.folder, filename)
                                blob = bucket.blob(path_to)
                                blob.upload_from_file(t)
                    successful |= rec

            #successful.cleanup()

        return super(DbBackup, self).action_backup()

    def action_gcloud_test_connection(self):
        """Check if the Gcloud settings are correct."""
        try:
            if self.sftp_connection():
                message = _("Connection Test Successful!")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': message,
                        'type': 'success',
                        'sticky': False,
                    }
                }
        except GC_exceptions.NotFound:
            msg = "Error: Sorry, that bucket (%s) does not exist!" % self.bucket_name
            _logger.info("Connection Test Failed!:" + msg, exc_info=True)
            raise exceptions.UserError(_("Connection Test Failed!\n " + msg))

    @api.depends("folder", "method", "sftp_host", "sftp_port", "sftp_user")
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            if rec.method == "local":
                rec.name = "%s @ localhost" % rec.folder
            elif rec.method == "sftp":
                rec.name = "sftp://%s@%s:%d%s" % (
                    rec.sftp_user, rec.sftp_host, rec.sftp_port, rec.folder)
            elif rec.method == "gcloud":
                rec.name = "Gloud: %s/%s" % (
                    rec.bucket_name, rec.folder)

    def cleanup(self):
        """Clean up old backups."""
        try:
            now = datetime.now()
            backups_to_keep = []

            # ---------------- last_seven_days ---------------------
            last_seven_days = []
            for i in range(15):
                a = now - timedelta(days=i)
                date_time_str = a.strftime("%Y_%m_%d")
                last_seven_days.append(date_time_str)

            # print("seven oldest : ", last_seven_days)
            # ----------------- last 4 mondays -----------------------
            last_four_mondays = []
            for i in range(4):
                monday = now - timedelta(days=now.weekday() + 7 * (i + 1))
                date_time_str = monday.strftime("%Y_%m_%d")
                last_four_mondays.append(date_time_str)
            # print("seven last_four_mondays : ", last_four_mondays)

            # ------------------- first day of last 3 months ------------

            first_day_of_last_three_months = []
            d = datetime.now()
            for month in range(1, 4):
                first_day_of_month = d.replace(day=1)
                last_day_of_previous_month = first_day_of_month - timedelta(days=1)
                first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

                first_day_of_last_three_months.append(
                    (first_day_of_previous_month.strftime("%Y_%m_%d")))

                d = first_day_of_previous_month

            # print("first day of last 3 months", first_day_of_last_three_months)

            backups_to_keep += last_seven_days
            backups_to_keep += last_four_mondays
            backups_to_keep += first_day_of_last_three_months

            # print("Backups to keep:", backups_to_keep)

            # -------------------Remove occurence from backups_to_keep list
            for d in backups_to_keep:
                if backups_to_keep.count(d) > 1:
                    backups_to_keep.remove(d)

            # print("Backups to keep:", backups_to_keep)

            local = self.filtered(lambda r: r.method == "local")
            if local:
                for rec in local:
                    with rec.cleanup_log():
                        # print("BACKUP ==>", rec)
                        delete = False
                        for name in (iglob(os.path.join(rec.folder, "*"))):
                            backup_name = os.path.basename(name)
                            # print(backup_name)
                            s = backup_name.split("_")[:3]
                            backup_date = "_".join(s)
                            # print("_".join(s))
                            if backup_date in backups_to_keep:
                                delete = True
                        if delete:
                            for name in (iglob(os.path.join(rec.folder, "*"))):
                                backup_name = os.path.basename(name)
                                # print(backup_name)
                                s = backup_name.split("_")[:3]
                                backup_date = "_".join(s)
                                # print("_".join(s))
                                if backup_date not in backups_to_keep:
                                    os.unlink(name)

            sftp = self.filtered(lambda r: r.method == "sftp")
            if sftp:
                for rec in sftp:
                    with rec.sftp_connection() as remote:
                        delete = False
                        for name in remote.listdir(rec.folder):
                            backup_name = os.path.basename(name)
                            # print(backup_name)
                            s = backup_name.split("_")[:3]
                            backup_date = "_".join(s)
                            if backup_date in backups_to_keep:
                                delete = True
                        if delete:
                            for name in remote.listdir(rec.folder):
                                backup_name = os.path.basename(name)
                                # print(backup_name)
                                s = backup_name.split("_")[:3]
                                backup_date = "_".join(s)
                                if backup_date not in backups_to_keep:
                                    remote.unlink('%s/%s' % (rec.folder, name))

            gcloud = self.filtered(lambda r: r.method == "gcloud")
            if gcloud:
                for rec in gcloud:
                    bucket = rec.sftp_connection()
                    if bucket:
                        blobs = bucket.list_blobs(prefix=rec.folder, delimiter=None)
                        blobs2 = bucket.list_blobs(prefix=rec.folder, delimiter=None)
                        # CHECK IF THERE IS AT LEAST ONE BACKUP IN BACKUPS TO KEEP BEFORE DELETE
                        delete = False
                        for blob in list(blobs):
                            backup_name = os.path.basename(blob.name)
                            s = backup_name.split("_")[:3]
                            backup_date = "_".join(s)
                            if backup_date in backups_to_keep:
                                delete = True

                        if delete:
                            for blob in blobs2:
                                backup_name = os.path.basename(blob.name)
                                s = backup_name.split("_")[:3]
                                backup_date = "_".join(s)
                                #if backup_date not in backups_to_keep:
                                    #blob.delete()
        except Exception as e:
            _logger.error(str(e))
            self.message_post(body=str(e))
