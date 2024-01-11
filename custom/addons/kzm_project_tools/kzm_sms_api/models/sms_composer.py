from odoo import models, api,fields, _
import requests
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SendSMS(models.TransientModel):
    _inherit = 'sms.composer'

    def _action_send_sms(self):
        """ Sending SMS using Bulk SMS API """

        if self.env.user.company_id.active_sms:
            api_url = "https://bulksms.ma/developer/sms/send"
            api_token = self.env.user.company_id.bulk_sms_key
            numbers = self.recipient_single_number_itf
            message = self.body

            if len(message) > 160:
                raise ValidationError("Le message ne doit pas dépasser 160 caractères.")


            data = {
                'token': api_token,
                'tel': numbers,
                'message': message,
            }

            response = requests.post(api_url, data=data)

            if response.status_code == 200:
                json_response = response.json()
                print(json_response)
                if 'success' in json_response and json_response['success'] == 1:

                    _logger.warning("--------------------->>>>> SMS Sent Successfully")

                elif 'error' in json_response:
                    if "Client" in json_response['error']:
                        # Handle the case where the token is missing or invalid
                        raise ValidationError("Invalid Token , or Token Not found")
                    elif "essai" in json_response['error']:
                        # Handle the case where the client is in trial period
                        raise ValidationError("During the trial period, you can only send messages to your own number.")
                    else:
                        # Handle other error cases
                        raise ValidationError("SMS Sent Failed! Response: %s" % response.text)

            _logger.warning("--------------------->>>>> DATA SMS")
            _logger.warning(data)

            _logger.warning("--------------------->>>>> RESPONSE SMS")
            _logger.warning(response.text)
        else:
            return super(SendSMS, self)._action_send_sms()