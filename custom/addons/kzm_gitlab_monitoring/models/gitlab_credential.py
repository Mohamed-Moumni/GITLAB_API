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
            vals['status'] = 'active'
            vals['name'] = gitlab_data.access_token_name
            vals['expiration_date'] = gitlab_data.expiration_date
        except:
            vals['status'] = 'not_Active'
        return super(GitlabCredential, self).create(vals)

    def validate(self):
        """
            validate the gitlab entred access_token
        """
        for record in self:
            token = record.token
            username = record.username
            try:
                gitlab_data = GitlabData(username, token)
                gitlab_data.authenticate()
                record.status = 'active'
            except:
                record.status = 'not_Active'

