from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import logging
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class MassMailing(models.Model):
    _inherit = 'mailing.mailing'

    @api.model
    def _process_mass_mailing_queue(self):

        if self.env.user.company_id.active_sms:
            for mailing in self.search([('state', 'in', ('in_queue', 'sending')),
                                        '|', ('schedule_date', '<', fields.Datetime.now()),
                                        ('schedule_date', '=', False)]):
                for contact_list in mailing.contact_list_ids:
                    # Créer une liste pour stocker les numéros de téléphone
                    phone_numbers = []

                    for contact in contact_list.contact_ids:
                        # Accéder au numéro de téléphone du contact
                        phone_number = contact.mobile  # Remplacez 'mobile' par le champ réel utilisé dans votre modèle
                        # Ajouter le numéro de téléphone à la liste
                        phone_numbers.append(phone_number)
                        # Votre logique personnalisée avec le numéro de téléphone

                    if phone_numbers and self.env.user.company_id.active_sms:
                        if self.env.user.company_id.active_sms:
                            api_url = "https://bulksms.ma/developer/sms/send"
                            api_token = self.env.user.company_id.bulk_sms_key
                            message = mailing.body_plaintext

                            if len(message) > 160:
                                raise ValidationError("Le message ne doit pas dépasser 160 caractères.")

                            # Convertir la liste de numéros de téléphone en chaîne séparée par des virgules
                            phone_numbers_str = ','.join(phone_numbers)

                            data = {
                                'token': api_token,
                                'tel': phone_numbers_str,
                                'message': message,
                            }

                            response = requests.post(api_url, data=data)

                            if response.status_code == 200:
                                json_response = response.json()
                                if 'success' in json_response and json_response['success'] == 1:
                                    _logger.warning("--------------------->>>>> SMS Sent Successfully")
                                    # Gérer la notification de succès si nécessaire
                                    mailing.message_post(body="SMS Sent Successfully")
                                elif 'error' in json_response:
                                    if "Client" in json_response['error']:
                                        # Afficher un avertissement dans le chatter
                                        mailing.message_post(body="Invalid Token , or Token Not found")
                                        _logger.warning("------>>> Invalid Token , or Token Not found")
                                    elif "essai" in json_response['error']:
                                        # Afficher un avertissement dans le chatter
                                        mailing.message_post(
                                            body="During the trial period, you can only send messages to your own number.")
                                        _logger.warning(
                                            "------>>> During the trial period, you can only send messages to your own number.")
                                    else:
                                        # Afficher un avertissement dans le chatter avec la réponse de l'API
                                        mailing.sudo().message_post(
                                            body="SMS Sent Failed! Response: %s" % response.text)
                                        _logger.warning("------>>> SMS Sent Failed! Response: %s" % response.text)

                            _logger.warning("--------------------->>>>> DATA SMS")
                            _logger.warning(data)

                            _logger.warning("--------------------->>>>> RESPONSE SMS")
                            _logger.warning(response.text)

                # Marquer le mailing comme "done" après l'envoi à tous les contacts associés
                mailing.write({
                    'state': 'done',
                    'sent_date': fields.Datetime.now(),
                    'kpi_mail_required': not mailing.sent_date,
                })

        else:
            return super(MassMailing, self)._process_mass_mailing_queue()
