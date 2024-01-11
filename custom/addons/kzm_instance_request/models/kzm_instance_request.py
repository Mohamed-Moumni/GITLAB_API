import random
import string
import logging
from odoo import models, fields, api, _, exceptions
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class kzmInstanceRequest(models.Model):
    _name = 'kzm.instance.request'
    _description = 'kzm instance request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Désignation', readonly=True)

    _sql_constraints = [
        ('address_ip', 'unique(address_ip)',
         'Each instance must have a unique IP address.'),
        ('name', 'unique(name)', 'Each Instance must have a unique name')
    ]
    address_ip = fields.Char('Adresse IP')
    active = fields.Boolean(string='active', default=True)
    cpu = fields.Char(string='cpu')
    ram = fields.Char(string='ram')
    disk = fields.Char(string='disk')
    url = fields.Char(string='url')
    state = fields.Selection([
        ('Brouillon', 'Brouillon'),
        ('Soumise', 'Soumise'),
        ('En traitement', 'En traitement'),
        ('Traitee', 'Traitée'),
    ], string="state", default="Brouillon", track_visibility='onchange')
    limit_date = fields.Date(
        string='Date limite de traitement', track_visibility='onchange')
    treat_date = fields.Datetime(string='Date de traitement ')
    treat_duration = fields.Float(
        string='Durée de traitement', compute="compute_treat_duration", store=True)
    partner_id = fields.Many2one('res.partner', string='Client')
    tl_id = fields.Many2one('hr.employee', string='employee')
    tl_user_id = fields.Many2one(
        'res.users', string='user_employee')
    odoo_id = fields.Many2one('odoo.version', string='Odoo Version')
    perimeters_ids = fields.Many2many(
        'perimeter.perimeter', string='Perimeters')
    perimeters_nums = fields.Integer(
        string="Number of Perimeter", compute="compute_perimeter_nums", store=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    @api.depends('treat_date')
    def compute_treat_duration(self):
        """Compute Treat Duration"""
        for record in self:
            if record.treat_date:
                duration = (record.treat_date - datetime.now()).total_seconds()
                record.treat_duration = float(divmod(duration, 86400)[0])

    @api.depends('perimeters_ids')
    def compute_perimeter_nums(self):
        """Compute Perimeter Nums"""
        for instance in self:
            instance.perimeters_nums = len(self.perimeters_ids)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'kzm_instance_request.sequence')
        result = super(kzmInstanceRequest, self).create(vals)
        return result

    def unlink(self):
        for record in self:
            if record.state != 'Brouillon':
                raise exceptions.UserError(
                    _("You can only delete instance requests in Brouillon state."))
        return super(kzmInstanceRequest, self).unlink()

    def write(self, values):
        for record in self:    
            if 'limit_date' in values:
                new_limit_date = fields.Date.from_string(
                    values['limit_date'])
                today = fields.Date.today()
                if new_limit_date and new_limit_date < today:
                    raise exceptions.UserError(
                        _("You cannot define a deadline before today."))
                record._schedule_activity()
            if 'state' in values and values['state'] == 'Traitee':
                values['treat_date'] = fields.Datetime.now()
            super(kzmInstanceRequest, record).write(values)

    @api.model
    def _schedule_activity(self):
        """Schedule an activity"""
        self.activity_schedule(
            'kzm_instance_request.activity_type_to_be_processed',
            note=_('hello'))

    def change_to_Brouillon(self):
        """Change the state to Brouillon"""
        print("Change to Brouillon")
        self.write({'state': 'Brouillon'})

    def change_to_Soumise(self):
        """Change the state to Soumise"""
        print("Change to Soumise")
        self.write({'state': 'Soumise'})

    def change_to_En_Traitement(self):
        """Change the state to En Traitement"""
        print("Change to En Traitement")
        self.write({'state': 'En traitement'})

    def change_to_Traitee(self):
        """Change the state to Traitee"""
        print("Change to Traitee")
        self.write({'state': 'Traitee'})

    def check_state_and_change(self):
        """check the state of the instance and if the condition about the datetime and change the state to soumise"""
        print("state changed to Soumise")
        now = fields.Date.today()
        limite_time_before_five_days = self.limit_date - timedelta(days=5)
        for record in self:
            if self.limit_date and now >= limite_time_before_five_days:
                record.change_to_Soumise()