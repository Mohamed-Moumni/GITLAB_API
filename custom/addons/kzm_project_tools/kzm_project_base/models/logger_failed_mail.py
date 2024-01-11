from odoo import fields, models, api


class LogerFailedMail(models.Model):
    _name = 'logger.failed.mail'
    _description = 'loger failed mail'

    name = fields.Char()
    message_id = fields.Char(string="message ID")
    client_mail = fields.Char(string="Client mail")
    date = fields.Char(string="sending date")
