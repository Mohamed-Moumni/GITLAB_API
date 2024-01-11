from odoo import fields, models, api
from xmlrpc import client as xmlrpclib
import email
import email.policy
import logging

_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 50
MAIL_TIMEOUT = 60


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'
    _description = 'fetchmail server'

    def fetch_mail_last_version(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        for server in self:
            _logger.info('start checking for new emails on %s server %s', server.server_type, server.name)
            additionnal_context['default_fetchmail_server_id'] = server.id
            count, failed = 0, 0
            imap_server = None
            pop_server = None
            connection_type = server._get_connection_type()
            if connection_type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            res_id = MailThread.with_context(**additionnal_context).message_process(
                                server.object_id.model, data[0][1], save_original=server.original,
                                strip_attachments=(not server.attach))
                        except Exception as e:
                            _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name,
                                         exc_info=True)
                            if isinstance(data[0][1], xmlrpclib.Binary):
                                data[0][1] = bytes(message.data)
                            if isinstance(data[0][1], str):
                                data[0][1] = message.encode('utf-8')
                            message = email.message_from_bytes(data[0][1], policy=email.policy.SMTP)

                            msg_dict = MailThread.message_parse(message, save_original=False)
                            self.env['logger.failed.mail'].create(
                                {'name': msg_dict['subject'], 'message_id': msg_dict['message_id'],
                                 'client_mail': msg_dict['email_from'], 'date': msg_dict['date']})

                            failed += 1
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count,
                                 server.server_type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type,
                                 server.name, exc_info=True)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            elif connection_type == 'pop':
                try:
                    while True:
                        failed_in_loop = 0
                        num = 0
                        pop_server = server.connect()
                        (num_messages, total_size) = pop_server.stat()
                        pop_server.list()
                        for num in range(1, min(MAX_POP_MESSAGES, num_messages) + 1):
                            (header, messages, octets) = pop_server.retr(num)
                            message = (b'\n').join(messages)
                            res_id = None
                            try:
                                res_id = MailThread.with_context(**additionnal_context).message_process(
                                    server.object_id.model, message, save_original=server.original,
                                    strip_attachments=(not server.attach))
                                pop_server.dele(num)
                            except Exception:
                                _logger.info('Failed to process mail from %s server %s.', server.server_type,
                                             server.name, exc_info=True)
                                failed += 1
                                if isinstance(message, xmlrpclib.Binary):
                                    message = bytes(message.data)
                                if isinstance(message, str):
                                    message = message.encode('utf-8')
                                message = email.message_from_bytes(message, policy=email.policy.SMTP)
                                msg_dict = MailThread.message_parse(message, save_original=False)
                                self.env['logger.failed.mail'].create(
                                    {'name': msg_dict['subject'], 'message_id': msg_dict['message_id'],
                                     'client_mail': msg_dict['email_from'], 'date': msg_dict['date']})
                                failed_in_loop += 1
                            self.env.cr.commit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", num,
                                     server.server_type, server.name, (num - failed_in_loop), failed_in_loop)
                        # Stop if (1) no more message left or (2) all messages have failed
                        if num_messages < MAX_POP_MESSAGES or failed_in_loop == num:
                            break
                        pop_server.quit()
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type,
                                 server.name, exc_info=True)
                finally:
                    if pop_server:
                        pop_server.quit()
            server.write({'date': fields.Datetime.now()})
        return True

    @api.model
    def _fetch_mails_last_version(self):
        """ Method called by cron to fetch mails from servers """
        return self.search([('state', '=', 'done'), ('server_type', '!=', 'local')]).fetch_mail_last_version()
