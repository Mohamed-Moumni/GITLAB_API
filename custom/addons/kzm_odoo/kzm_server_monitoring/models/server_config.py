import subprocess
from datetime import datetime
from datetime import timedelta

import paramiko
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class server_config(models.Model):
    _name = "odoo.server.config"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'server_config'

    name = fields.Char(string='Configuration Name')
    responsible_id = fields.Many2one('res.users', string='Responsible', required=True)

    hostname = fields.Char(string='Hostname')
    username = fields.Char(string='Username')
    private_key = fields.Char(string='Private Key',
                              default='/home/ubuntu/.ssh/id_rsa')
    cmd_path = fields.Char(
        default='/opt/odoo/custom/karizma_tools/server_monitoring_info.sh')

    max_day = fields.Integer(string='Maximal Day', default=1)

    check_date = fields.Datetime(string='Checking Date', default=fields.Datetime.now)
    date_start = fields.Datetime(string='Start Date', compute='_compute_dates')
    date_stop = fields.Datetime(string='Stop Date', compute='_compute_dates')

    host_name = fields.Char(string='Host Name')

    ram_capacity = fields.Float(string='RAM Capacity', default=1)
    ram_available = fields.Float(string='RAM Available')
    ram_consumption = fields.Float(string='RAM Consumption %',
                                   compute='_compute_ram_consumption', store=True)
    ram_consumption_text = fields.Char(string='RAM Consumption (texte) %',
                                       compute='_compute_ram_consumption', store=True)
    max_ram_consumption = fields.Float(string='Max RAM Consumption', default=100)

    disk_capacity = fields.Float(string='DISK Capacity', default=1)
    disk_used = fields.Float(string='DISK usage (GIB)')
    disk_used_text = fields.Char(string='DISK usage (GIB)',
                                 compute='_compute_disk_used')
    disk_available = fields.Float(string='DISK Available')
    disk_consumption = fields.Float(string='DISK Consumption',
                                    compute='_compute_disk_consumption')
    disk_consumption_text = fields.Char(string='DISK Consumption',
                                        compute='_compute_disk_consumption')

    cpu_number = fields.Float(string='CPU Number')
    cpu_consumption = fields.Float(string='CPU Consumption %')
    cpu_consumption_text = fields.Char(string='CPU Consumption %',
                                       compute='_compute_cpu_consumption')
    max_cpu_consumption = fields.Float(string='Max CPU Consumption', default=100)
    cpu_freq = fields.Float(string='CPU Frequency')
    cpu_freq_min = fields.Float(string='CPU Minimal Frequency')
    cpu_freq_max = fields.Float(string='CPU Maximal Frequency')

    ping_status = fields.Boolean(string='Network Status')

    state = fields.Selection([("0", "NOK"), ("1", "OK")], string='Host State',
                             compute='_compute_host_consumption', store=True)
    color = fields.Integer(string='State Color', compute='_compute_host_color')

    @api.depends('check_date')
    def _compute_dates(self):
        for r in self:
            if r.check_date:
                d = fields.Datetime.from_string(r.check_date)
                r.date_start = d + timedelta(hours=-1)
                r.date_stop = d + timedelta(hours=1)

    @api.depends('state')
    def _compute_host_color(self):
        for r in self:
            if r.state == '0':
                r.color = 1
            else:
                r.color = -1

    @api.depends('cpu_consumption')
    def _compute_cpu_consumption(self):
        for r in self:
            r.cpu_consumption_text = str("%.2f" % r.cpu_consumption) + "%"

    @api.depends('disk_used')
    def _compute_disk_used(self):
        for r in self:
            r.disk_used_text = str("%.2f" % r.disk_used) + " GIB"

    @api.depends('ram_capacity', 'ram_available')
    def _compute_ram_consumption(self):
        for r in self:
            r.ram_consumption = 100.0 * (1 - r.ram_available / r.ram_capacity)
            r.ram_consumption_text = str("%.2f" % r.ram_consumption) + "%"

    @api.depends('disk_capacity', 'disk_available')
    def _compute_disk_consumption(self):
        for r in self:
            r.disk_consumption = 100.0 * (1 - r.disk_available / r.disk_capacity)
            r.disk_consumption_text = str("%.2f" % r.disk_consumption) + "%"

    @api.depends('disk_available', 'ram_consumption', 'cpu_consumption')
    def _compute_host_consumption(self):
        for r in self:
            if r.disk_available < 2 or r.ram_consumption > 90 or r.cpu_consumption > 90 or r.ping_status == False:
                r.state = '0'
            else:
                r.state = '1'

    # CONNECT TO THE SERVER
    def server_connection(self, config):
        try:
            k = paramiko.RSAKey.from_private_key_file(config.private_key)
        except Exception as e:
            raise ValidationError(
                _("Private key does not exist, make a valid path!") + "%s" % (
                    str(e)))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            c.connect(hostname=config.hostname, username=config.username, pkey=k)
        except:
            raise ValidationError(_(
                "Connection Failed, Check the hostname, username or the private key!"))
        return c

    # CREATE INSTANCE FROM CONFIG
    def create_instance(self):
        config = self.env['odoo.server.config'].browse(self.id)
        ext_data = {
            'name': config.host_name,
            'check_date': config.check_date,
            'date_start': config.date_start,
            'date_stop': config.date_stop,
            'host_name': config.host_name,
            'ram_capacity': config.ram_capacity,
            'ram_available': config.ram_available,
            'ram_consumption': config.ram_consumption,
            'ram_consumption_text': config.ram_consumption_text,
            'max_ram_consumption': config.max_ram_consumption,
            'disk_capacity': config.disk_capacity,
            'disk_used': config.disk_used,
            'disk_used_text': config.disk_used_text,
            'disk_available': config.disk_available,
            'disk_consumption': config.disk_consumption,
            'disk_consumption_text': config.disk_consumption_text,
            'cpu_number': config.cpu_number,
            'cpu_consumption': config.cpu_consumption,
            'cpu_consumption_text': config.cpu_consumption_text,
            'max_cpu_consumption': config.max_cpu_consumption,
            'cpu_freq': config.cpu_freq,
            'cpu_freq_min': config.cpu_freq_min,
            'cpu_freq_max': config.cpu_freq_max,
            'ping_status': config.ping_status,
            'state': config.state,
            'color': config.color,
            'server_config': config.id
        }
        self.env["odoo.instance.monitoring"].create(ext_data)

    # UPDATE CONFIG
    def update_config(self):
        config = self.env['odoo.server.config'].browse(self.id)
        if config:
            c = self.server_connection(config)
            stdin, stdout, stderr = c.exec_command("source " + config.cmd_path)
            info = str(stdout.read()).replace(',', '.').split(';')
            ping_status = c.exec_command("ping -c 1 " + config.hostname)
            try:
                config.check_date = datetime.now()
                config.host_name = info[1] if info[1] else 'N/A'
                config.cpu_consumption = float(info[2]) if info[2] else 0
                config.cpu_number = int(info[3]) if info[3] else 0
                config.ram_capacity = float(info[4]) if info[4] else 0
                config.ram_available = float(info[5]) if info[5] else 0
                config.disk_capacity = float(info[6]) if info[6] else 0
                config.disk_used = float(info[7]) if info[7] else 0
                config.disk_available = float(info[8]) if info[8] else 0
                config.cpu_freq = float(info[9]) if info[9] else 0
                config.cpu_freq_min = float(info[10]) if info[10] else 700
                config.cpu_freq_max = float(info[11]) if info[11] else 3100
                config.ping_status = ping_status
            except Exception as e:
                raise ValidationError(_('Error : ') + "%s" % str(e))
            c.close()

    # BUTTON REFRESH
    def refresh_config(self):
        config = self.env['odoo.server.config'].browse(self.id)
        if config:
            config.update_config()
            config.create_instance()

    # TEST PING
    def ping_config(self):
        for r in self:
            try:
                out = subprocess.check_output(['ping', '-c', '1', r.hostname])
                print(out)
            except:
                raise ValidationError(
                    _("NOK!"))
            raise ValidationError(
                _("OK!"))

    # CRON JOB UPDATE ALL
    def invoke_cron_job(self):
        all_config = self.env['odoo.server.config'].search([])
        print(all_config)
        for config in all_config:
            config.update_config()
            config.create_instance()

    @api.model
    def create(self, vals):
        rec = super(server_config, self).create(vals)
        mail_activity_dt = 'mail.mail_activity_data_todo'
        if (rec.disk_available < 2):
            rec.activity_schedule(mail_activity_dt,
                                  summary=_("Check the instance [DISK]"),
                                  note=_("There are only %.2f GIB available in %.2f "
                                         "GIB" % (
                                             rec.disk_available, rec.disk_capacity)),
                                  user_id=rec.responsible_id.id)
        elif (rec.ram_consumption > 90):
            rec.activity_schedule(mail_activity_dt,
                                  summary=_('Check the instance [RAM]'),
                                  note=_("RAM consumption reaches %.2f" %
                                         rec.ram_consumption + "%"),
                                  user_id=rec.responsible_id.id)
        elif (rec.cpu_consumption > 90):
            rec.activity_schedule(mail_activity_dt,
                                  summary=_('Check the instance [CPU]'),
                                  note=_("CPU consumption reaches %.2f" %
                                         rec.cpu_consumption + "%"),
                                  user_id=rec.responsible_id.id)
        return rec

    def write(self, vals):
        super(server_config, self).write(vals)
        for key, value in vals.items():
            K = (f'{key}')
            V = (f'{value}')
            if K == 'disk_available' and float(V) < 2:
                self.activity_schedule('mail.mail_activity_data_todo',
                                       summary=_("Check the instance [DISK]"),
                                       note=_(
                                           "There are only %.2f GIB available in %.2f GIB" % (
                                               float(V), self.disk_capacity)),
                                       user_id=self.responsible_id.id)

            if K == 'cpu_consumption' and float(V) > 90:
                self.activity_schedule('mail.mail_activity_data_todo',
                                       summary=_("Check the instance [CPU]"),
                                       note=_("CPU consumption reaches %.2f" %
                                              float(V) + "%"),
                                       user_id=self.responsible_id.id)

            if K == 'ram_available':
                ram_consumption = (1 - (float(V) / self.ram_capacity)) * 100
                if ram_consumption > 90:
                    self.activity_schedule('mail.mail_activity_data_todo',
                                           summary=_("Check the instance [RAM]"),
                                           note=_(
                                               "RAM consumption reaches %.2f" % ram_consumption + "%"),
                                           user_id=self.responsible_id.id)
