# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import urllib.request as urllib2
import os
import shutil
import xmlrpc.client

from odoo import models, fields, _
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from odoo.exceptions import UserError
import io
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import logging

_logger = logging.getLogger(__name__)
try:
    import xlrd
except ImportError:
    xlrd = xlsx = None


class ImportWizard(models.TransientModel):
    _name = 'import.wizard'
    _description = 'Import Image Wizard'

    def _get_model_domain(self):
        models = []
        for m in self.env['ir.model'].search([("transient", "=", False)]):
            if 'binary' in m.field_id.mapped('ttype'):
                models.append(m.id)
        return [("id", "in", models)]

    google_auth_api_folder = fields.Char(related='company_id.google_auth_api_folder', store=1)
    type = fields.Selection([('csv', 'Excel File'), ('google', 'Google Drive'), ('rpc', 'XML-RPC')], default='csv',
                            string="Importation type")

    model_id = fields.Many2one("ir.model", string="Model", domain=lambda s: s._get_model_domain())
    field_id = fields.Many2one('ir.model.fields', string='Field to import')
    file = fields.Binary('File to import')
    folder_id = fields.Char("Folder ID")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    canevas_name = fields.Char(string='Filename')
    result = fields.Text(string="Result")
    imported = fields.Boolean("Imported")
    source_folder = fields.Char("Source folder")
    error_folder = fields.Char("Error folder")
    on_server = fields.Boolean("Images on server")
    url = fields.Char("Url")
    db = fields.Char("DB")
    username = fields.Char("Login")
    password = fields.Char(string='Password')
    ######################################################
    secret_client_google = fields.Char(string='Secret client google')
    credential_name = fields.Char(string='Name file save credential')
    page_token = fields.Char(string='Token page for drives shared')
    field_research_id = fields.Many2one('ir.model.fields', string='Field to research')
    block_importation = fields.Boolean("Block importation")

    def _search_record(self, sid):
        splited_name = str(sid).split('.')
        record = False
        f_search = str(self.field_research_id.name)
        if not f_search and len(splited_name) == 2:
            record = self.env['ir.model.data'].search(
                [('name', '=', splited_name[1]), ('module', '=', splited_name[0]), ('model', '=', self.model_id.model)])

        if record:
            return self.env[self.model_id.model].browse(record.res_id)
        else:
            if self.field_research_id.ttype == 'integer':
                record = self.env[self.model_id.model].search([(f_search, '=', int(sid))])

            if self.field_research_id.ttype in ['char', 'text']:
                record = self.env[self.model_id.model].search([(f_search, '=', str(sid))])

        return record

    def import_file(self):
        self.imported = False
        ids = []
        f_search = str(self.field_research_id.name)
        if self.type == 'csv':
            if 'csv' not in self.canevas_name:
                wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
                for sheet in wb.sheets():
                    for row in range(1, sheet.nrows):
                        sid = sheet.cell(row, 0).value
                        record = self._search_record(sid)
                        if not record:
                            if not self.result:
                                self.result = 'Enregistrement %s manquant.' % sid
                            else:
                                self.result += '\n Enregistrement %s manquant.' % sid
                        else:
                            value = sheet.cell(row, 1).value

                            if value:
                                try:
                                    if "http://" in value or "https://" in value:
                                        link = urllib2.urlopen(value).read()
                                        image_data = base64.encodebytes(link)
                                    else:
                                        with open(value, 'rb') as image:
                                            image_data = base64.b64encode(image.read()).decode('ascii')
                                    if image_data:
                                        record.write({
                                            self.field_id.name: image_data
                                        })
                                except Exception as e:
                                    if not self.result:
                                        self.result = 'Erreur - %s' % str(e)
                                    else:
                                        self.result += '\n Erreur - %s' % str(e)
                            else:
                                if not self.result:
                                    self.result = 'Valeur non définie pour la ligne  %s manquant.' % row
                                else:
                                    self.result += '\n Valeur non définie pour la ligne  %s manquant.' % row
        elif self.type == 'google':
            self.imported = False
            credentials_path = {
                "type": "service_account",
                "project_id": "thematic-gift-242113",
                "private_key_id": "f56a33a6d17219184acb0cb434a7bbc1628cc407",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC59jLEMp5UqXS6\nSNms2LpJxUJ65eP27qChZwf7ieJ5V3MjthEd5i7EjVWNVxm55C/vommtZkcLBJHd\npnmdGw3uPZbegDwcxle8PdBRuuNzAwAHCCCzPnRT6aLW4OXGBeBEeyxiUQjo43xr\n2ayzVEIVkWgCpxdG8CFh/y3E7C91Q1/sI127yPuudAyN3H8nvkgsnu9P/ORIiin/\nObK6z373v1zfyGY9aaIC8QN9FvlgZl39eEyDgU2D1JHPSCWiTG1ZwtaLEgH1N5Qi\nNZ428ArgGzypiHO5marA/3flLgISutWacNYgDi81/jqscIJl66Eo6eMmAbSdvEpq\n47N8tQPnAgMBAAECggEAMAvMpQVhBAW+O20cFHzwcKPvH7qq0f9ocBsjJFnFMk2m\nWXkuZfe1aKINkxWId49d1T+0pxDwVQfqugZLkIxPZpjyFG20WkjinSepXZx4LJx/\nUtHGRRljS9Tm9jaoFygof/kFCCfgse8ok+LrLHAeHN1zLpBGQtVDAsM/64uMXXLH\n702Ln/5iGypTik1HSmi6VxSgN8E+RZgF/GZ57tW3NDdXL4vEP2X6lqYNK9ZTmjyr\nBzGOyCvmXZvPX4mTiJsULJlfgXgEj3Syfp55Rtfqb5NlqQlkeCKpIAREmVgX0E/+\ngCdqS7kC1W3mHt8Mv2tkPW3zPROe+vxkb2C7Pbo1aQKBgQD0BV/5xf+BEJmxf8Fn\nR+wquI6FcOODdMbfCi5HeoLoyM028rNp86j109fPmdFR6DfwvMeMAHU36amsSmLx\nuM0+KJh2lZucbcy9DMc0lGTt4vhdTd/ZfmW6VA92l10g1IvwYocjVM7UhAmRogR0\nIqlym7TPsdm/tDI9wk0kGdAYvwKBgQDDFzBxoIBeyDWeFxTkpCdngDheQSNPmBth\nsIbKlBILvbZqP/q4OHQHG1niRTRZ/951ijg9b37rSM9zUEhQOCqDuAhVSY2eZDGv\nIJrHzjQpFYKlmPMbq8DT7H81ibTU/ZFvcqahxoxmK9cj1urJp2GLInUxSGd8OXG/\nQOSYIhh22QKBgEviEAKATAA6xVCpRd90QkDWu5tLi7Spb96UL+gSdPsm1oor1xcv\nqm8nvYjVcH5kFGFMk1E6IzmL9DObvkElEs4tmZvm0klG69AuVRRIwUootsttGBtu\nbvwOf/CFCXTYI9xRB205RkhX9xHOrEvhK4h0WznrOKegxa7m6U48qLXJAoGBALWd\nVtnQwvB5jYCYmDipoI03zkHgfdDRF1yAC1t3ML2BZNnQqcTpuQoMqkZ8ilnmWuAt\nRmHa89pxM75z1H3pa5qnrgpHqPD08VPJFI5BJknA3pjupBL0d1RSa7IZeiB11fhc\nUUd1IKrU0TlqD7Sef64Y6+RvNPduOrgC30vJIeExAoGBAJ6mi+vV1Nh1LUtm5WMZ\nLHBtoumEoM1tHET3O1uTthIEpyXb4CTLXkCmB8ELVj0FGYVMTp3x2o0tXD8b5gsO\nsJ6mf4HqJSAeMHgR8qwdVXdHE4upfNiGPdyxsTyCn+f8G3CkFx9MXKhxA+dlbMQ+\njceLN5k7XIHS7T1gWkQcjkG5\n-----END PRIVATE KEY-----\n",
                "client_email": "kzm-storage@thematic-gift-242113.iam.gserviceaccount.com",
                "client_id": "101472600942717197097",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kzm-storage%40thematic-gift-242113.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }
            # ID of the Google Drive folder containing the images
            folder_id = self.folder_id
            ids = []

            # Initialize credentials and Drive API client
            credentials = service_account.Credentials.from_service_account_info(credentials_path, scopes=[
                'https://www.googleapis.com/auth/drive.readonly'])
            drive_service = build('drive', 'v3', credentials=credentials)

            # Retrieve the list of files in the folder
            response = drive_service.files().list(
                q=f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/gif')",
                fields='files(id, name)'
            ).execute()

            _logger.info("response ======> %s" % response)
            if not response:
                raise UserError("Aucunes images dans le dossier communiqué")
            # Process the list of image files
            for file in response['files']:
                file_id = file['id']
                file_name = file['name']
                _logger.info("======================> Formatted name %s" % file_name)
                splited_name = file_name.split('.')
                splited_name[-1] = False
                _logger.info(splited_name)
                name = '.'.join([d for d in splited_name if d])
                _logger.info("======================> Formatted name %s" % name)
                record_id = self._search_record(name)
                if record_id:
                    request = drive_service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                    image_base64 = base64.b64encode(fh.getvalue())
                    record_id.write({
                        self.field_id.name: image_base64
                    })
                    ids.append(record_id.id)

                else:
                    if self.block_importation:
                        raise UserError("%s non existant sur la base" % name)
                    else:
                        if not self.result:
                            self.result = 'Valeur non définie pour la ligne  %s manquant.' % name
                        else:
                            self.result += '\n Valeur non définie pour la ligne  %s manquant.' % name

            # gauth = GoogleAuth()
            # GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = "{}".format(self.secret_client_google)
            # # "/opt/odoo15/custom/addons/karizma_tools/kzm_image_import/models/client_secrets.json".format()
            # # print("{}.txt".format(self.credential_name))
            # gauth.LoadCredentialsFile("{}".format(self.credential_name))
            # if gauth.credentials is None:
            #     gauth.LocalWebserverAuth()
            # elif gauth.access_token_expired:
            #     gauth.Refresh()
            # else:
            #     gauth.Authorize()
            #
            # gauth.SaveCredentialsFile("{}".format(self.credential_name))
            # drive = GoogleDrive(gauth)
            # file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(self.page_token)}).GetList()
        elif self.type == 'rpc':
            path = self.source_folder
            dest = self.error_folder
            for filename in os.listdir(path):
                with open(os.path.join(path, filename), "rb") as attachment_file:
                    image_Base = base64.b64encode(attachment_file.read()).decode('ascii')
                    splited_name = filename.split('.')
                    splited_name[-1] = False
                    _logger.info(splited_name)
                    name = '.'.join([d for d in splited_name if d])
                    # name = name.replace("_PHOTO1", "")
                    _logger.info("======================> New name %s" % name)
                    if not self.on_server:
                        mod_init = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
                        mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
                        uid = mod_init.authenticate(self.db, self.username, self.password, {})
                        try:
                            rec = False
                            if len(splited_name) >= 3 and not f_search:
                                rec = mod.execute_kw(self.db, uid, self.password,
                                                     'ir.model.data', 'search_read',
                                                     [[['name', '=', splited_name[1]],
                                                       ['module', '=', splited_name[0]],
                                                       ['model', '=', self.model_id.model]]],
                                                     {'fields': ['res_id'], 'limit': 1})
                            if not rec:
                                if self.field_research_id.ttype == 'integer':
                                    record_id = mod.execute_kw(self.db, uid,
                                                               self.password,
                                                               self.model_id.model,
                                                               'search',
                                                               [[[f_search, '=', int(name)]]])

                                if self.field_research_id.ttype in ['char', 'text']:
                                    record_id = mod.execute_kw(self.db, uid,
                                                               self.password,
                                                               self.model_id.model,
                                                               'search',
                                                               [[[f_search, '=', name]]])
                        except Exception as e:
                            _logger.info(str(e))
                            continue
                        if record_id:
                            mod.execute_kw(self.db, uid, self.password, self.model_id.model, 'write',
                                           [record_id, {self.field_id.name: image_Base}])
                    else:
                        record_id = self._search_record(name)
                        if record_id:
                            record_id.write({
                                self.field_id.name: image_Base
                            })
                            _logger.info("====================> recoord_id %s" % record_id.id)
                    if not record_id and path != dest:
                        shutil.copyfile(os.path.join(path, filename), os.path.join(dest, filename))
                        if self.block_importation:
                            raise UserError(_("%s est inexistant sur votre base" % name))

        if self.result:
            self.imported = True
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
        else:
            msgs = "%s imported with success" %(len(ids))
            _logger.info("===================> %s " % msgs)
        # self.imported = True
        # if self.result:
        #     raise UserError(self.result)
        # new_wizard = self.env['import.wizard'].create(
        #     {'model_id': self.model_id.id, 'type': self.type, 'file': self.file, 'result': self.result,
        #      'canevas_name': self.canevas_name, 'field_id': self.field_id.id, 'folder_id': self.folder_id,
        #      'imported': self.imported})
        # view_id = self.env.ref('kzm_image_import.product_import_image_wizard_form_view').id
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'import.wizard',
        #     'view_mode': 'form',
        #     'res_id': new_wizard.id,
        #     'views': [(view_id, 'form')],
        #     'target': 'new',
        # }
