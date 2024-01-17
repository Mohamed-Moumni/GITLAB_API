from odoo import models, fields, _, exceptions
import gitlab
from .gitlab_data import GitlabData
from typing import List
import logging

logger = logging.getLogger(__name__)


class ProjectGitlab(models.Model):
    """
        project Gitlab model contains all the attributes needed from for the Gitlab api
        and also the business logic

    Args:
        models (models.Model): odoo orm model class
    """
    _inherit = "project.database"

    git_link = fields.Char('Git Link', required=True)
    branch_number = fields.Integer(string="Branch Number", readonly=True)
    group = fields.Char('Group', readonly=True)
    project_name = fields.Char('Project Name', readonly=True)
    default_branch = fields.Char('Default Branch', readonly=True)
    last_merge_request = fields.Char('Last Merge Request', readonly=True)
    pipeline_status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('undefined', 'Undefined'),
    ], string='Pipeline Status', readonly=True)
    quality_code = fields.Float('Quality Code', readonly=True)

    git_lab_credential_id = fields.Many2one(
        'gitlab.credential', string='Git Lab Token', required=True)
    members_ids = fields.Many2many(
        'gitlab.user', string="Members", readonly=True)

    def synchronization(self):
        """Synchronize with gitlab and get all the data needed"""

        gitlab_credentials = self.env['gitlab.credential'].search(
            [('id', '=', self.git_lab_credential_id.id)])
        if gitlab_credentials:
            try:
                gitlabData = GitlabData(gitlab_credentials.token)
                gitlabData.get_gitlab_infos(self.git_link)
                self.update_Gitlab_data(gitlabData)
            except Exception as e:
                raise exceptions.UserError(
                    f'Encountring error while getting Data from Gitlab: {e}')
        else:
            raise exceptions.UserError('Credentials is Not Valid')

    def update_Gitlab_data(self, gitlabData) -> None:
        """
            update Gitlab data infos
        Args:
            gitlabData (Gitlabdata): gitlabData objec infos
        """
        self.write({'branch_number': gitlabData.branch_number})
        self.write({'group': gitlabData.group})
        self.write({'project_name': gitlabData.project_name})
        self.write({'default_branch': gitlabData.default_branch})
        self.write({'last_merge_request': gitlabData.last_merge_request})
        self.write({'pipeline_status': gitlabData.pipeline_status})
        self.write({'members_ids': [
                   (6, 0, self.get_gitlab_members(gitlabData.get_gitlab_members()))]})

    def get_gitlab_members(self, members: List[str]):
        """
            gitlab project members 
        Args:
            members (list[str]): gitlab members

        Returns:
            list[str]: gitlab_members ids
        """

        gitlab_members: list[str] = []
        for member in members:
            memberExist = self.env['gitlab.user'].search(
                [('gitlab_id', '=', member.id)])

            if len(memberExist) == 0:
                gitlab_user_id = self.env['gitlab.user'].create(
                    {'name': member.name, 'username': member.username, 'gitlab_id': member.id, 'avatar': member.avatar_url}).id
                gitlab_members.append(gitlab_user_id)
            else:
                gitlab_members.append(memberExist[0].id)
        return gitlab_members

    def calculate_quality_code(self):
        """
            calculate quality code of the last commit
        """

        gitlab_credentials = self.env['gitlab.credential'].search(
            [('id', '=', self.git_lab_credential_id.id)])
        if gitlab_credentials:
            try:
                gitlabData = GitlabData(gitlab_credentials.token)
                gitlabData.get_gitlab_infos(self.git_link)
                if gitlabData.pipeline_id != None:
                    self.write({'quality_code': gitlabData.get_quality_code()})
            except Exception as e:
                raise exceptions.UserError(
                    f'Encountring error while getting Data from Gitlab: {e}')
        else:
            raise exceptions.UserError('Credentials is Not Valid')

    def project_sync(self):
        self.synchronization()
        self.calculate_quality_code()

    def gitlab_cron(self):
        gitlab_projects = self.env['project.database'].search([])
        for project in gitlab_projects:
            try:
                project.with_delay().project_sync()
            except Exception as e:
                raise exceptions.Warning(
                    _("Gitlab synchronization Failed!\n " + str(e)))
