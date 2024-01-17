from odoo import models, fields, api, exceptions
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
    active = fields.Boolean(default=True)
    token = fields.Char('Token', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('not_Active', 'Not Active'),
    ], string='Status')
    expiration_date = fields.Char('Expiration Date')
    
    _sql_constraints = [
        ('token', 'unique(token)', 'This gitlab Token already used.')
    ]

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
            gitlabData = GitlabData(vals['token'])
            vals['name'] = gitlabData.access_token_name
            vals['token'] = gitlabData.token
            vals['status'] = 'active'
            vals['expiration_date'] = gitlabData.expiration_date
        except Exception as e:
            raise exceptions.UserError(f'Credentials Authentication Error: {e}')
        return super(GitlabCredential, self).create(vals)
    
    def write(self, vals):
        try:
            gitlabData = GitlabData(vals['token'])
            vals['name'] = gitlabData.access_token_name
            vals['token'] = gitlabData.token
            vals['status'] = 'active'
            vals['expiration_date'] = gitlabData.expiration_date
        except Exception as e:
            raise exceptions.UserError(
                f'Credentials Authentication Error: {e}')
        return super(GitlabCredential, self).write(vals)

