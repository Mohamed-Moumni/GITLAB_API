[![Build Status](https://travis-ci.com/karizmaconseil/Template.svg?token=3rLzMkGSCCyiQHepEdQM&branch=master)](https://travis-ci.com/karizmaconseil/Template)

# Dépôt contenant les fonctionnalités de base KARIZMA (Odoo version: 16.0)

### Pré-requis

* Ce dépôt utilise les modules
  * [auditlog](https://github.com/OCA/server-tools/tree/16.0/auditlog) défini sur le
    dépôt [auditlog](https://github.com/OCA/server-tools/tree/16.0/auditlog)
  * [auto_backup](https://github.com/OCA/server-tools/tree/16.0/auto_backup) défini sur le
    dépôt [kzm_odoo](https://github.com/OCA/server-tools/tree/16.0/auto_backup)
  * [queue_job](https://github.com/OCA/queue/tree/16.0/queue) défini sur le
    dépôt [OCA/queue](https://github.com/OCA/queue/tree/16.0)
* Installer le fichier [requirement.txt](https://github.com/KARIZMACONSULTING/kzm_hr/blob/16.0/requirements.txt) pour
  utiliser les dépendances des pointages

### Changements
* Le module account_fiscal_year a été totalement supprimé
* Le module kzm_account_fiscalyear_type a été totalement supprimé
* Le module account_fiscal_period ajoute par fichier data, les types de périodes fiscales
  * Année => date.range.type.unit_of_time == '0'
  * Trimestre => date.range.type.unit_of_time == '1' avec date.range.type.duration_count == 3
  * Mois => date.range.type.unit_of_time == '1' avec date.range.type.duration_count == 1
  * Quinzaine => date.range.type.unit_of_time == '3' avec date.range.type.duration_count == 15
* Le champs fiscal_year du module account_fiscal_year est à remplacer par unit_of_time == '0'
* La génération des périodes doit passer par le wizard **Generate Date Ranges**



