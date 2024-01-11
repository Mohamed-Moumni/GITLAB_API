# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import xmlrpc.client
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class KzmControleDataMaster(models.Model):
    _inherit = 'database.metadata'
    _description = 'Master Controle Data Ping'

    client_authentication = fields.Selection([('login', 'User'), ('key', 'Clé API')],
                                             string="S'authentifier avec", required=True, default='login', )
    api_key = fields.Char()
    nmbr_users = fields.Integer(string='Nombre d\'utilisateurs')
    nbr_active_users = fields.Integer(string='Nombre d\'utilisateurs actifs')
    nbr_share_users = fields.Integer(string='Nombre d\'utilisateurs partagés')
    database_expiration_date = fields.Text(string='Date d\'expiration de la base de données')
    nbr_active_share_users = fields.Integer(string='Nombre d\'utilisateurs partagés actifs')
    url = fields.Char(string='Client URL')

    # link = fields.Char(related='project_database_id.link')
    # protocole = fields.Selection(related='project_database_id.protocole')

    @api.onchange('client_authentication')
    def onchange_client_authentication(self):
        if self.client_authentication == 'key':
            self.password = self.api_key

        if self.client_authentication == 'login':
            ps = self.password
            self.password = ps

    @api.onchange('api_key')
    def onchange_api_key(self):
        if self.client_authentication == 'key':
            self.password = self.api_key

        if self.client_authentication == 'login':
            ps = self.password
            self.password = ps

    def update_notification(self):

        if self.client_authentication == 'login':
            password = self.password
        if self.client_authentication == 'key':
            password = self.api_key

        db_name = self.name
        if db_name and self.url and password and self.user:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            uid = common.authenticate(db_name, self.user, password, {})
            if uid:
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
                result = models.execute_kw(db_name, uid, password, 'publisher_warranty.contract',
                                           'update_notification', [3])

                message = models.execute_kw(db_name, uid, password, 'publisher_warranty.contract',
                                            'get_public_message', [])

                self.message_post(
                    body="Le Ping Odoo a été bien fait pour la base de données {}. <br> <span style='color:red;'>JSON Envoyé : </span>{}".format(
                        self.name, message),
                    message_type='comment',
                )

    def sync_client_parameters(self):

        if self.client_authentication == 'login':
            password = self.password
        if self.client_authentication == 'key':
            password = self.api_key

        db_name = self.name
        if db_name and self.url and password and self.user:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            uid = common.authenticate(db_name, self.user, password, {})

            if uid:
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

                # Obtenir les valeurs actuelles des paramètres ir.config
                remote_values = {}
                keys_to_fetch = ['kzm.number', 'kzm.number_active', 'kzm.number_share', 'kzm.number_active_share',
                                 'database.expiration_date']

                try:
                    for key in keys_to_fetch:
                        id_param = models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'search',
                                                     [[('key', '=', key)]], {'limit': 1})
                        value = models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'read',
                                                  [id_param], {'fields': ['value']})
                        remote_values[key] = value[0]['value']
                except IndexError:
                    raise ValidationError('Merci de vérifier l\'existence de  paramètres Ping ou '
                                          'veuillez installer le module : Contrôle Data Ping sur la base Client!')

                return remote_values
            else:
                raise ValidationError('Authentication Failed!')
        else:
            raise ValidationError('Veuillez remplir les champs : DB name , Client Url, Login, Password Svp.!')

    def sync_value_from_remote_config(self):

        # Cette fonction remplit les champs du formulaire avec les valeurs récupérées de la base distante
        remote_values = self.sync_client_parameters()

        self.nmbr_users = remote_values.get('kzm.number', 0)
        self.nbr_active_users = remote_values.get('kzm.number_active', 0)
        self.nbr_share_users = remote_values.get('kzm.number_share', 0)
        self.nbr_active_share_users = remote_values.get('kzm.number_active_share', 0)
        self.database_expiration_date = remote_values.get('database.expiration_date', '')

    def sync_parameters(self):

        if self.client_authentication == 'login':
            password = self.password
        if self.client_authentication == 'key':
            password = self.api_key

        db_name = self.name
        nbr_users = self.nmbr_users
        nbr_active_users = self.nbr_active_users
        nbr_share_users = self.nbr_share_users
        database_expiration_date = self.database_expiration_date
        nbr_active_share_users = self.nbr_active_share_users

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(db_name, self.user, password, {})

        _logger.warning("--------------------->>>>> UID")
        _logger.warning(uid)

        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

            # Obtenir l'ID de kzm.number,etc.. depuis l'instance client.
            id_kzm_number = models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'search',
                                              [[('key', '=', 'kzm.number')]], {'limit': 1})
            models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'write', [id_kzm_number, {
                'value': nbr_users
            }])

            id_kzm_number_active = models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'search',
                                                     [[('key', '=', 'kzm.number_active')]], {'limit': 1})
            models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'write',
                              [id_kzm_number_active, {
                                  'value': nbr_active_users
                              }])

            id_kzm_number_share = models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'search',
                                                    [[('key', '=', 'kzm.number_share')]], {'limit': 1})
            models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'write',
                              [id_kzm_number_share, {
                                  'value': nbr_share_users
                              }])

            id_kzm_active_share = models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'search',
                                                    [[('key', '=', 'kzm.number_active_share')]], {'limit': 1})
            models.execute_kw(db_name, uid, password, 'ir.config_parameter', 'write',
                              [id_kzm_active_share, {
                                  'value': nbr_active_share_users
                              }])

            # id_expiration_date = models.execute_kw(self.db_name, uid, self.password, 'ir.config_parameter', 'search',
            #                                        [[('key', '=', 'database.expiration_date')]], {'limit': 1})
            # models.execute_kw(self.db_name, uid, self.password, 'ir.config_parameter', 'write',
            #                   [id_expiration_date, {
            #                       'value': database_expiration_date
            #                   }])

            self.message_post(
                body="Les paramétres sont bien synchronisé pour la base de données {}".format(self.name),
                message_type='comment')
            # raise ValidationError('La synchronisation des paramètres a été effectuée avec succès.!')
        else:
            raise ValidationError('Authentication Failed!')
