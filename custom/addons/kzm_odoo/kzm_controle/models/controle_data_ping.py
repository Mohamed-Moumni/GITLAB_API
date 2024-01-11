from odoo import models, fields, api
import datetime
import logging

import requests
import werkzeug.urls

from ast import literal_eval

from odoo import api, release, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.models import AbstractModel
from odoo.tools.translate import _
from odoo.tools import config, misc, ustr

_logger = logging.getLogger(__name__)


class KzmControleDataPing(AbstractModel):
    _inherit = "publisher_warranty.contract"

    @api.model
    def _get_message(self):
        Users = self.env['res.users']
        IrParamSudo = self.env['ir.config_parameter'].sudo()

        dbuuid = IrParamSudo.get_param('database.uuid')
        db_create_date = IrParamSudo.get_param('database.create_date')
        limit_date = datetime.datetime.now()
        limit_date = limit_date - datetime.timedelta(15)
        limit_date_str = limit_date.strftime(misc.DEFAULT_SERVER_DATETIME_FORMAT)
        if "share" in Users._fields:
            nbr_share_users = Users.search_count([("share", "=", True), ('active', '=', True)])
            nbr_active_share_users = Users.search_count(
                [("share", "=", True), ("login_date", ">=", limit_date_str), ('active', '=', True)])
        user = self.env.user
        domain = [('application', '=', True), ('state', 'in', ['installed', 'to upgrade', 'to remove'])]
        apps = self.env['ir.module.module'].sudo().search_read(domain, ['name'])

        set_param = self.env['ir.config_parameter'].sudo().set_param
        enterprise_code = IrParamSudo.get_param('database.enterprise_code')

        # Paramètres modifiables
        kzm_nbr_users = self.env['ir.config_parameter'].sudo().get_param('kzm.number')
        kzm_nbr_active_users = self.env['ir.config_parameter'].sudo().get_param('kzm.number_active')
        kzm_nbr_share_users = self.env['ir.config_parameter'].sudo().get_param('kzm.number_share')
        nbr_active_share_users = self.env['ir.config_parameter'].sudo().get_param('kzm.number_active_share')
        existing_expiration_date = self.env['ir.config_parameter'].sudo().get_param('database.expiration_date')

        new_expiration_date = datetime.datetime(2030, 10, 10)
        formatted_date = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')

        #if not existing_expiration_date:
        #    set_param('database.expiration_date', formatted_date)
        if not kzm_nbr_users:
            set_param('kzm.number', 10)
        if not kzm_nbr_active_users:
            set_param('kzm.number_active', 10)
        if not kzm_nbr_share_users:
            set_param('kzm.number_share', 10)
        if not nbr_active_share_users:
            set_param('kzm.number_active_share', 10)

        web_base_url = IrParamSudo.get_param('web.base.url')
        msg = {
            "dbuuid": dbuuid,
            "nbr_users": kzm_nbr_users,
            "nbr_active_users": kzm_nbr_active_users,
            "nbr_share_users": kzm_nbr_share_users,
            "nbr_active_share_users": nbr_active_share_users,
            "dbname": self._cr.dbname,
            "db_create_date": db_create_date,
            "version": release.version,
            "language": user.lang,
            "web_base_url": web_base_url,
            "apps": [app['name'] for app in apps],
            "enterprise_code": enterprise_code,
        }
        if user.partner_id.company_id:
            company_id = user.partner_id.company_id
            msg.update(company_id.read(["name", "email", "phone"])[0])

        _logger.warning("--------------------->>>>> MESSAGE")
        _logger.warning(msg)


        return msg

    @api.model
    def get_public_message(self):
        msg = self._get_message()
        msg.pop('maintenance', None)
        return msg

    @api.model
    def _get_sys_logs(self):
        """
        Utility method to send a publisher warranty get logs messages.
        """
        url = config.get("publisher_warranty_url")
        _logger.warning(url)
        msg = self._get_message()
        msg.pop('maintenance', None)
        #msg = super(KzmControleDataPing, self)._get_message()
        arguments = {'arg0': ustr(msg), "action": "update"}
        _logger.warning(arguments)

        r = requests.post(url, data=arguments, timeout=30)

        r.raise_for_status()
        _logger.warning(r)
        return literal_eval(r.text)

    def update_notification(self, cron_mode=True):
        try:
            try:
                result = self._get_sys_logs()
            except Exception:
                if cron_mode:  # we don't want to see any stack trace in cron
                    return False
                _logger.debug("Exception while sending a get logs messages", exc_info=1)
                raise UserError(_("Error during communication with the publisher warranty server fr. !! ZAKARIA"))
            # old behavior based on res.log; now on mail.message, that is not necessarily installed
            user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
            poster = self.sudo().env.ref('mail.channel_all_employees')
            if not (poster and poster.exists()):
                if not user.exists():
                    return True
                poster = user
            for message in result["messages"]:
                try:
                    poster.message_post(body=message, subtype_xmlid='mail.mt_comment', partner_ids=[user.partner_id.id])
                except Exception:
                    pass

        except Exception:
            if cron_mode:
                return False  # we don't want to see any stack trace in cron
            else:
                raise

        result = self._get_sys_logs()
        _logger.warning("-------->>> RESULT")
        _logger.warning(result)
        if result.get('enterprise_info'):
            out = result.get('enterprise_info')
            set_param = self.env['ir.config_parameter'].sudo().set_param
            set_param('database.expiration_date', result['enterprise_info'].get('expiration_date'))
            set_param('database.expiration_reason', result['enterprise_info'].get('expiration_reason', 'trial'))
            set_param('database.enterprise_code', result['enterprise_info'].get('enterprise_code'))
            set_param('database.already_linked_subscription_url',
                      result['enterprise_info'].get('database_already_linked_subscription_url'))
            set_param('database.already_linked_email',
                      result['enterprise_info'].get('database_already_linked_email'))
            set_param('database.already_linked_send_mail_url',
                      result['enterprise_info'].get('database_already_linked_send_mail_url'))
            _logger.warning(out)
        return True
