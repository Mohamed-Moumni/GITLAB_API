from odoo import models, fields, _
from odoo.exceptions import UserError
import gitlab
from .utils import gitlab_authenticate, get_project_namespace, get_gitlab_infos


class ProjectGitlab(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    _inherit = "project.database"

    git_link = fields.Char('Git Link')
    branch_number = fields.Integer(string="Branch Number", readonly=True)
    group = fields.Char('Group')
    project_name = fields.Char('Group')
    default_branch = fields.Char('Default Branch')
    git_lab_credential_id = fields.Many2one(
        'gitlab.credential', string='Git Lab Token')
    last_merge_request = fields.Char('Last Merge Request')
    pipeline_status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('no_pipeline', 'No Pipeline')
    ], string='Pipeline Status')

    def synchronization(self):
        """Synchronize with gitlab and get all the data needed"""

        # protect against the empty gitlab.credential model
        gitlab_credentials = self.env['gitlab.credential'].search(
            [('id', '=', self.git_lab_credential_id.id)])
        if gitlab_credentials:
            credentials = {
                'username': gitlab_credentials.username,
                'token': gitlab_credentials.token,
                'status': gitlab_credentials.status
            }
            if credentials['status'] == 'active':
                try:
                    git_lab_infos = get_gitlab_infos(
                        self.git_link, credentials['token'])
                    self.branch_number = git_lab_infos['branch_number']
                    self.group = git_lab_infos['group']
                    self.project_name = git_lab_infos['project_name']
                    self.default_branch = git_lab_infos['default_branch']
                    self.last_merge_request = git_lab_infos['last_merge_request']
                    self.pipeline_status = git_lab_infos['pipeline_status']
                except:
                    raise UserError(_('Credentials is not Active'))
            else:
                raise UserError(_('Credentials is not Active'))
        else:
            raise UserError(_('Credentials is not Active'))

    def calculate_quality_code(self):
        pass
    # project_members
    # code_rating
