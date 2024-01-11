from odoo import models, fields


class instance_monitoring(models.Model):
    _name = 'odoo.instance.monitoring'
    _description = 'client_instance_monitoring'
    _order = 'check_date'

    name = fields.Char(string='Name')

    check_date = fields.Datetime(string='Checking Date', default=fields.Datetime.now)
    date_start = fields.Datetime(string='Start Date')
    date_stop = fields.Datetime(string='Stop Date')

    host_name = fields.Char(string='Host Name')

    ram_capacity = fields.Float(string='RAM Capacity')
    ram_available = fields.Float(string='RAM Available')
    ram_consumption = fields.Float(string='RAM Consumption %')
    ram_consumption_text = fields.Char(string='RAM Consumption %')
    max_ram_consumption = fields.Float(string='Max RAM Consumption', default=100)

    disk_capacity = fields.Float(string='DISK Capacity')
    disk_used = fields.Float(string='DISK usage (Gib)')
    disk_used_text = fields.Char(string='DISK usage (Gib)')
    disk_available = fields.Float(string='DISK Available')
    disk_consumption = fields.Float(string='DISK Consumption')
    disk_consumption_text = fields.Char(string='DISK Consumption')

    cpu_number = fields.Float(string='CPU Number')
    cpu_consumption = fields.Float(string='CPU Consumption %')
    cpu_consumption_text = fields.Char(string='CPU Consumption %')
    max_cpu_consumption = fields.Float(string='Max CPU Consumption', default=100)
    cpu_freq = fields.Float(string='CPU Frequency')
    cpu_freq_min = fields.Float(string='CPU Minimal Frequency')
    cpu_freq_max = fields.Float(string='CPU Maximal Frequency')

    ping_status = fields.Boolean(string='Network Status')

    state = fields.Selection([("0", "NOK"), ("1", "OK")], string='Host State',
                             store=True)
    color = fields.Integer(string='State Color')

    server_config = fields.Many2one('odoo.server.config', string='Server Configuration',
                                    ondelete='cascade')
