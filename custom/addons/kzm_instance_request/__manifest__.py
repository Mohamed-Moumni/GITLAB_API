{
    'name': "kzm_instance_request",
    'summary': "Karizma Module",
    'description': """ un module complet de demande de création d’instance avec des profils de demandeur, de responsable et d’administrateur.""",
    'author': "Mohamed Moumni",
    'license': "AGPL-3",
    'category': 'Uncategorized',
    'version': '16.0',
    'depends': ['base', 'mail', 'contacts', 'sale_management', 'hr', 'web_gantt', 'portal', 'website', 'web'],
    'data': [
        # data related files
        'data/odoo_versions_data.xml',
        'data/cron.xml',
        'data/sequence.xml',
        'data/data_activity.xml',
        'data/email_template.xml',
        'data/perimeter_data.xml',
        # security files
        'security/instance_groups.xml',
        'security/ir.model.access.csv',
        # kzm_instance_request views
        'views/kzm_instance_request/kzm_instance_request_view.xml',
        'views/kzm_instance_request/kzm_instance_request_form.xml',
        'views/kzm_instance_request/kzm_instance_request_search.xml',
        'views/kzm_instance_request/kzm_instance_request.xml',
        # odoo version views
        'views/odoo_version/odoo_version_view.xml',
        'views/odoo_version/odoo_version_form.xml',
        'views/odoo_version/odoo_version_search.xml',
        'views/odoo_version/odoo_version.xml',
        # perimeter views
        'views/perimeter/perimeter.xml',
        'views/hr_employee/hr_employee_view.xml',
        'views/hr_employee/hr_employee.xml',
        'views/quotations/quotations_view.xml',
        'views/quotations/quotations_search.xml',
        'wizard/instance_wizard_view_form.xml',
        'reports/instance_demand_report.xml',
        'reports/instance_demand_report_template.xml',
        'views/kzm_instance_request/kzm_instance_request_template.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': True,
    'installable': True
}
