from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class MassSMSTest(models.TransientModel):
    _inherit = 'mailing.sms.test'

    def action_send_sms(self):
        if self.env.user.company_id.active_sms:
            api_url = "https://bulksms.ma/developer/sms/send"
            api_token = self.env.user.company_id.bulk_sms_key
            numbers = self.numbers

            # Split numbers by lines and sanitize
            numbers_list = [number.strip() for number in numbers.splitlines()]
            sanitize_res = phone_validation.phone_sanitize_numbers_w_record(numbers_list, self.env.user)
            sanitized_numbers = [info['sanitized'] for info in sanitize_res.values() if info['sanitized']]

            message = self.mailing_id.body_plaintext
            tels = ','.join(sanitized_numbers)
            _logger.warning("--------------------->>>>> Phones Numbers : ", tels)

            if len(message) > 160:
                raise ValidationError("Le message ne doit pas dépasser 160 caractères.")

            data = {
                'token': api_token,
                'tel': ','.join(sanitized_numbers),  # Join sanitized numbers with commas
                'message': message,
            }

            response = requests.post(api_url, data=data)

            if response.status_code == 200:
                json_response = response.json()
                if 'success' in json_response and json_response['success'] == 1:
                    _logger.warning("--------------------->>>>> SMS Sent Successfully")
                    raise ValidationError("SMS TEST Sent Successfully")

                elif 'error' in json_response:
                    if "Client" in json_response['error']:
                        raise ValidationError("Invalid Token , or Token Not found")
                    elif "essai" in json_response['error']:
                        raise ValidationError("During the trial period, you can only send messages to your own number.")
                    else:
                        raise ValidationError("SMS Sent Failed! Response: %s" % response.text)

            _logger.warning("--------------------->>>>> DATA SMS")
            _logger.warning(data)

            _logger.warning("--------------------->>>>> RESPONSE SMS")
            _logger.warning(response.text)
        else:
            # Call the original action_send_sms from the parent class
            return super(MassSMSTest, self).action_send_sms()

