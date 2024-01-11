# encoding: utf-8
##############################################################################
#
#    Localisation marocaine module for OpenERP, Localisation marocaine, Les bases
#    Copyright (C) 2014 (<http://www.example.org>) Anonym
#
#    This file is a part of Localisation marocaine
#
#    Localisation marocaine is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Localisation marocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields

# The two variable are related to kzm_ma_tax/models/tax_engine.py
# Think to update all
ENCAISSEMENT = 'payments'
DEBIT = 'invoices'


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = 'Company'

    patente = fields.Char(string='Patente', size=64, help='Patente', related="partner_id.patente_code", readonly=False)
    forme_juridique_id = fields.Many2one("res.company.forme.juridique", string='Forme juridique', )
    activity = fields.Char(string="", size=64, help='Activity')
    cnss = fields.Char(string='CNSS', size=64, help='CNSS')
    cimr = fields.Char(string='CIMR', size=64, help='CIMR')
    vat = fields.Char(string='Identifiant fiscal', size=64, )
    ice = fields.Char(string='ICE', size=15, related="partner_id.ice", readonly=False)
    #     company_registry = fields.Char(string=u'Registre de commerce', size=64,)
    identifiant_tp = fields.Char(string='Identifiant TP', size=64, )
    commune_id = fields.Many2one("l10n.ma.commune", string='Commune', )
    declaration_type = fields.Selection(
        [('m', 'Mensuelle'), ('t', 'Trimestrielle')], 'Type de la declaration',
        required=True, default='m')
    based_on = fields.Selection(
        [(DEBIT, 'Debit'), (ENCAISSEMENT, 'Encaissement'), ], 'Regime', required=True,
        default=ENCAISSEMENT)
    fax = fields.Char(string="")
    capital = fields.Float(string="")
    cin_partenaire_obligatoire = fields.Boolean("CIN Obligatoire pour Partenaire")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cin_partenaire_obligatoire = fields.Boolean(string="CIN Obligatoire pour Partenaire",
                                                related="company_id.cin_partenaire_obligatoire", readonly=False)
    module_kzm_duplicate_base_safe = fields.Boolean("Dupliquer les bases de données sans serveurs/cron", default=True)
    module_kzm_database_cleanup = fields.Boolean("Pouvoir supprimer toutes les données", default=True)
    module_oca_auto_backup_extension = fields.Boolean("Activer le backup automatisé")
    module_kzm_queue_backup = fields.Boolean("Activer la gestion des backups avec les fils d'attente")
    module_kzm_backup = fields.Boolean("Activer l'interface de backup")
    module_kzm_mail_office_365 = fields.Boolean("Activer la MAJ Office 365")
    module_kzm_image_import = fields.Boolean("Activer l'import d'image")


class ResCompanyFormeJuridique(models.Model):
    _name = 'res.company.forme.juridique'
    _description = 'Formes juridiques'

    name = fields.Char(string='Nom', size=64, required=True, )
    code = fields.Char(string='Code Juridic', size=64, required=True, )
