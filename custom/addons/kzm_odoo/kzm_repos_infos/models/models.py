# -*- coding: utf-8 -*-

from github import Github

from odoo import models, fields


class ModuleInfo(models.Model):
    _name = 'module.info'
    _description = 'Information about a module'

    name = fields.Char("Module name")
    repository = fields.Char("Repository")
    url = fields.Char("Url")
    has_a_readme = fields.Boolean()
    description = fields.Text("Description")
    notes = fields.Text("Notes")

    def synchronize_modules_infos(self):
        self.env['res.config.settings'].synchronize_modules_infos()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    access_token = fields.Char(config_parameter='kzm_repos_infos.access_token', string='Token Github',
                               help='Fill with your github token', copy=True, default='', store=True)

    def queue_synchro(self):
        self.env['res.config.settings'].with_delay().synchronize_modules_infos()

    def synchronize_modules_infos(self):
        access = self.env['ir.config_parameter'].sudo().get_param('kzm_repos_infos.access_token', self.access_token)
        if access:
            g = Github(access)
            repos = g.get_user().get_repos("")
            # repo = g.get_repo("karizmaconseil/hestim")
            ModuleInfo = self.env['module.info']
            for repo in repos:
                try:
                    contents = repo.get_contents("")
                    for content_file in contents:
                        if content_file.type == "dir" and content_file.name not in ['OCA', 'karizmaconseil']:

                            infos = {
                                'name': content_file.name,
                                'repository': repo.html_url,
                                'url': content_file.html_url,
                                'has_a_readme': "README.md" in [f.name for f in repo.get_contents(content_file.path)]
                            }
                            existing_info = ModuleInfo.search([('name', '=', content_file.name)])
                            if existing_info:
                                existing_info.write(infos)
                            else:
                                ModuleInfo.create(infos)
                except Exception as e:
                    print(str(e))
