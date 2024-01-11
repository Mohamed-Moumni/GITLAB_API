# -*- coding: utf-8 -*-

import base64
import logging
import os
import traceback
import xmlrpc.client as xmlrpclib
from contextlib import contextmanager
from datetime import datetime, timedelta
from glob import iglob

from fabric import Connection
from odoo import _, api, exceptions, fields, models, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')


class Instance(models.Model):
    _name = 'kzm.instance'
    _description = "Instance name"
    _inherit = "mail.thread"

    @api.model
    def _default_user(self):
        return self.env['res.users'].browse(self.env.uid)

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    name = fields.Char(
        # compute="_compute_name",
        store=True,
        help="Summary of this backup process",
    )

    folder = fields.Char(
        default=lambda self: self._default_folder(),
        help='Absolute path for storing the backups',
        required=True
    )
    host = fields.Char(string="Host", )
    user = fields.Char(string="User", )
    port = fields.Char("Port", )
    ssh_key = fields.Text(string="Password")

    db_name = fields.Char(string="DB name")
    db_user = fields.Char(string="DB user")
    db_port = fields.Integer(string="DB port")
    password_user_db = fields.Char(string="Password user")
    master_password = fields.Char(string="Master Password")

    method = fields.Selection(
        [("local", "Local disk"), ("sftp", "Remote SFTP server")],
        default="local",
        help="Choose the storage method for this backup.",
    )
    days_to_keep = fields.Integer(
        required=True,
        default=0,
        help="Backups older than this will be deleted automatically. "
             "Set 0 to disable autodeletion.",
    )
    color = fields.Integer(default=6)
    sftp_host = fields.Char(
        'SFTP Server',
        help=(
            "The host name or IP address from your remote"
            " server. For example 192.168.0.1"
        )
    )
    sftp_port = fields.Integer(
        "SFTP Port",
        default=22,
        help="The port on the FTP server that accepts SSH/SFTP calls."
    )
    sftp_user = fields.Char(
        'Username in the SFTP Server',
        help=(
            "The username where the SFTP connection "
            "should be made with. This is the user on the external server."
        )
    )
    sftp_password = fields.Char(
        "SFTP Password",
        help="The password for the SFTP connection. If you specify a private "
             "key file, then this is the password to decrypt it.",
    )
    sftp_private_key = fields.Char(
        "Private key location",
        help="Path to the private key file. Only the Odoo user should have "
             "read permissions for that file.",
    )

    send_by_sftp = fields.Boolean("Send by SFTP")

    backup_format = fields.Selection(
        [
            ("zip", "zip (includes filestore)"),
            ("dump", "pg_dump custom format (without filestore)"),
            ("sql", "SGBD pg_dump custom format (without filestore)")
        ],
        default='zip',
        help="Choose the format for this backup."
    )

    backup_ids = fields.One2many("kzm.backup", 'instance_id', string="Backup")

    user_id = fields.Many2one('res.users', required=True, default=_default_user)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=_get_default_company_id, required=True)

    @api.model
    def _default_folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(tools.config["data_dir"], self.env.cr.dbname)

    def ssh_connection(self):
        self.ensure_one()
        host = self.host
        user = self.user

        _logger.debug(
            "Trying to connect to %s@%s with SSH" % (user, host),
        )

        connect_kwargs = {'password': self.ssh_key}

        # return Connection(**params)
        return Connection('%s@%s' % (user, host), connect_kwargs=connect_kwargs)

    def action_backup(self):
        # backup = None
        successful = self.browse()
        for rec in self:
            # test = False
            dbname = rec.db_name
            dbuser = rec.db_user
            # host = rec.host
            # port = rec.port
            pswd_user = rec.password_user_db
            filename = self.filename(datetime.now(), ext=rec.backup_format)
            with rec.backup_log():
                # Directory must exist
                try:
                    os.makedirs(rec.folder)
                except OSError:
                    pass

                path = os.path.join(rec.folder, filename)
                if rec.backup_format == "sql":
                    try:
                        cnx = rec.ssh_connection()
                        cmd = 'export PGPASSWORD=%s && mkdir -p %s && pg_dump -U %s  ' \
                              '%s > %s' % (
                                  pswd_user, rec.folder, dbuser, dbname, path
                              )

                        res = cnx.run(cmd)
                        print(res)
                        self.env['kzm.backup'].create({
                            "name": dbname,
                            "path": path,
                            "date": datetime.now(),
                            "statut": "success",
                            "instance_id": rec.id
                        })

                    except Exception as e:
                        self.env['kzm.backup'].create({
                            "name": dbname,
                            "path": path,
                            "date": datetime.now(),
                            "statut": "failed : " + str(e),
                            "instance_id": rec.id
                        })
                        self.send_mail_template()

                else:
                    try:
                        if not os.path.exists(rec.folder + "/" + rec.db_name):
                            os.makedirs(rec.folder + "/" + rec.db_name)

                        # path = os.path.join(rec.folder, rec.db_name)
                        path = os.path.join(rec.folder + "/" + rec.db_name, filename)

                        sock = xmlrpclib.ServerProxy(
                            'http://' + rec.host + ':' + rec.port + '/xmlrpc/db')
                        all_database = sock.list()
                        print(all_database)
                        backup_file = open(path, 'wb')

                        if rec.db_name in all_database:
                            dump = base64.b64decode(
                                sock.dump(rec.master_password, rec.db_name,
                                          rec.backup_format))
                            print(dump)
                            backup_file.write(dump)
                            backup_file.close()
                            self.env['kzm.backup'].create({
                                "name": dbname,
                                "path": path,
                                "date": datetime.now(),
                                "statut": "success",
                                "instance_id": rec.id

                            })
                            successful |= rec
                        else:
                            msg = "No Database named %s in this host." % rec.db_name
                            raise ValidationError(msg)

                        if rec.send_by_sftp:
                            with rec.sftp_connection() as remote:
                                # Directory must exist
                                try:
                                    path_dst = "//home//" + rec.sftp_user + \
                                               "//Backup//" + rec.db_name
                                    remote.makedirs(path_dst)
                                    remote.put(path, path_dst + "//" + filename)
                                except pysftp.ConnectionException:
                                    pass

                    except Exception as e:
                        # if test:
                        #     msg = "No Database named %s in this host." % rec.db_name
                        #     raise ValidationError(msg)

                        self.env['kzm.backup'].create({
                            "name": dbname,
                            "path": path,
                            "date": datetime.now(),
                            "statut": "failed : " + str(e),
                            "instance_id": rec.id
                        })
                        self.send_mail_template()
        successful.cleanup()

    @contextmanager
    def backup_log(self):
        """Log a backup result."""
        try:
            _logger.info("Starting database backup: %s", self.name)
            yield
        except Exception:
            _logger.exception("Database backup failed: %s", self.name)
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(  # pylint: disable=translation-required
                "<p>%s</p><pre>%s</pre>" % (
                    _("Database backup failed."),
                    escaped_tb),
                subtype=self.env.ref(
                    "auto_backup.mail_message_subtype_failure"
                ),
            )
        else:
            _logger.info("Database backup succeeded: %s", self.name)
            self.message_post(body=_("Database backup succeeded."))

    @staticmethod
    def filename(when, ext='zip'):
        """Generate a file name for a backup.

        :param datetime.datetime when:
            Use this datetime instead of :meth:`datetime.datetime.now`.
        :param str ext: Extension of the file. Default: dump.zip
        """
        return "{:%Y_%m_%d_%H_%M_%S}.{ext}".format(
            when, ext='dump.zip' if ext == 'zip' else ext
        )

    @api.depends("folder")
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            rec.name = "%s/%s" % (rec.folder, rec.db_name)

    def ping(self):
        for rec in self:
            rec.cnx = self.ssh_connection()
            rec.cnx.run("ping %s", self.host)

    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('kzm_backup.kzm_backup_email_template1')

        mail = self.env['mail.template'].browse(template.id)

        mail_id = mail.send_mail(self.id, force_send=True)

    def cleanup(self):
        """Clean up old backups."""
        now = datetime.now()
        for rec in self.filtered("days_to_keep"):
            with rec.cleanup_log():
                oldest = self.filename(now - timedelta(days=rec.days_to_keep))

                for name in iglob(os.path.join(rec.folder + "/" + rec.db_name,
                                               "*.dump.zip")):
                    if os.path.basename(name) < oldest:
                        os.unlink(name)

    def sftp_connection(self):
        """Return a new SFTP connection with found parameters."""
        self.ensure_one()
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        params = {
            "host": self.sftp_host,
            "username": self.sftp_user,
            "port": self.sftp_port,
            "cnopts": cnopts,
        }
        _logger.debug("Trying to connect to sftp://%(username)s@%(host)s:%(port)d",
                      extra=params)
        if self.sftp_private_key:
            params["private_key"] = self.sftp_private_key
            if self.sftp_password:
                params["private_key_pass"] = self.sftp_password
        else:

            params["password"] = self.sftp_password
            # params["cnopts"] = cnopts

        return pysftp.Connection(**params)

    def action_sftp_test_connection(self):
        """Check if the SFTP settings are correct."""
        try:
            # Just open and close the connection
            with self.sftp_connection():
                raise exceptions.Warning(_("Connection Test Succeeded!"))
        except (pysftp.CredentialException,
                pysftp.ConnectionException,
                pysftp.SSHException):
            _logger.info("Connection Test Failed!", exc_info=True)

        raise exceptions.Warning(_("Connection Test Failed!"))

    @contextmanager
    def cleanup_log(self):
        """Log a possible cleanup failure."""
        self.ensure_one()
        try:
            _logger.info(
                "Starting cleanup process after database backup: %s",
                self.name)
            yield
        except Exception:
            _logger.exception("Cleanup of old database backups failed: %s")
            escaped_tb = tools.html_escape(traceback.format_exc())
            # self.message_post(  # pylint: disable=translation-required
            #     "<p>%s</p><pre>%s</pre>" % (
            #         _("Cleanup of old database backups failed."),
            #         escaped_tb),
            #     subtype=self.env.ref("auto_backup.failure")
            # )
        else:
            _logger.info(
                "Cleanup of old database backups succeeded: %s",
                self.name)
