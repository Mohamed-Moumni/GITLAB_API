from odoo import models, fields, api
import gitlab
from .utils import gitlab_authenticate


class GitlabCredential(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    _name = "gitlab.credential"

    name = fields.Char('Token Name')
    username = fields.Char('Username')
    active = fields.Boolean(default=True)
    token = fields.Char('Token')
    status = fields.Selection([
        ('active', 'Active'),
        ('not_Active', 'Not Active'),
    ], string='Status')
    expiration_date = fields.Char('Expiration Date')
    
    # To Fix Later
    # def write(self, vals):
    #     for record in self:
    #         try:
    #             gl = gitlab_authenticate("https://gitlab.com", record.token)
    #             record.status = 'active'
    #             record.name = gl.personal_access_tokens.get("self").name
    #             record.expiration_date = gl.personal_access_tokens.get("self").expires_at
    #         except:
    #             record.status = 'not_Active'
    #     return super(GitlabCredential, self).write(vals)

    @api.model
    def create(self, vals):
        """_summary_

        Args:
            vals (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            gl = gitlab_authenticate("https://gitlab.com", vals['token'])
            vals['status'] = 'active'
            vals['name'] = gl.personal_access_tokens.get("self").name
            vals['expiration_date'] = gl.personal_access_tokens.get(
                "self").expires_at
        except:
            
            vals['status'] = 'not_Active'
        return super(GitlabCredential, self).create(vals)

    def validate(self):
        """_summary_
        """
        for record in self:
            token = record.token
            username = record.username
            try:
                gl = gitlab_authenticate("https://gitlab.com", token)
                record.status = 'active'
            except:
                record.status = 'not_Active'


