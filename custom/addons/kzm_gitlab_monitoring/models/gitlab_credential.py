from odoo import models, fields, api
import gitlab
from .gitlab_data import GitlabData

class GitlabCredential(models.Model):
    """
        Gitlab Credential model

    Args:
        models (models.Model): odoo model ORM

    Returns:
        _type_: Gitlab Credential object
    """
    _name = "gitlab.credential"

    name = fields.Char('Token Name')
    username = fields.Char('Username', required=True)
    active = fields.Boolean(default=True)
    token = fields.Char('Token', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('not_Active', 'Not Active'),
    ], string='Status')
    expiration_date = fields.Char('Expiration Date')

    @api.model
    def create(self, vals):
        """
            creation of gitlab credentials
        Args:
            vals (_type_):
            {
                'username':,
                'token':,
            }

        Returns:
            GitlabData: the created gitlab Credential
        """
        try:
            gitlab_data = GitlabData(vals['username'], vals['token'])
            gitlab_data.authenticate()
            gitlab_data.get_access_token_name()
            gitlab_data.get_expiration_date()
            vals['status'] = 'active'
            vals['name'] = gitlab_data.access_token_name
            vals['expiration_date'] = gitlab_data.expiration_date
        except:
            vals['name'] = "Unknown"
            vals['status'] = 'not_Active'
        return super(GitlabCredential, self).create(vals)

    def validate(self):
        """
            validate the gitlab entred access_token
        """
        token = self.token
        username = self.username
        try:
            gitlab_data = GitlabData(username, token)
            gitlab_data.authenticate()
            gitlab_data.get_access_token_name()
            gitlab_data.get_expiration_date()
            self.name = gitlab_data.access_token_name
            self.status = 'active'
            self.expiration_date = gitlab_data.expiration_date
        except:
            self.name = "Unknown"
            self.status = 'not_Active'

