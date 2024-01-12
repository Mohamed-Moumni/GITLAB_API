from odoo import models, fields, _, exceptions
import gitlab
from .gitlab_data import GitlabData

class ProjectGitlab(models.Model):
    """
        project Gitlab model contains all the attributes needed from for the Gitlab api
        and also the business logic

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
    
    members_ids = fields.Many2many('gitlab.user', string="Members", readonly=True)

    def synchronization(self):
        """Synchronize with gitlab and get all the data needed"""

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
                    git_lab_infos = GitlabData(credentials['username'], credentials['token'])
                    git_lab_infos.get_gitlab_infos(self.git_link)
                    self.write({'branch_number':git_lab_infos.branch_number})
                    self.write({'group': git_lab_infos.group})
                    self.write({'project_name': git_lab_infos.project_name})
                    self.write({'default_branch': git_lab_infos.default_branch})
                    self.write({'last_merge_request': git_lab_infos.last_merge_request})
                    self.write({'pipeline_status': git_lab_infos.pipeline_status})
                    self.write({'members_ids': [(6,0,self.get_gitlab_members(git_lab_infos.get_gitlab_members()))]})
                    
                except Exception as e:
                    raise exceptions.UserError(f'Encountring error while getting Data from Gitlab: {e}')
            else:
                raise exceptions.UserError(f'Credentials is not Active: {e}')
        else:
            raise exceptions.UserError(f'Credentials Not Found: {e}')
    
    def get_gitlab_members(self, members:list[str]):
        gitlab_members:list[str] = []
        for member in members:
            memberExist = self.env['gitlab.user'].search([('gitlab_id', '=', member.id)])
            
            if len(memberExist) == 0:
                gitlab_user_id = self.env['gitlab.user'].create({'name':member.username, 'username':member.username, 'gitlab_id':member.id}).id
                gitlab_members.append(gitlab_user_id)
            else:
                #pay attention to this line of code you have to refactor it asap
                gitlab_members.append(memberExist[1].id)
        return gitlab_members

    def calculate_quality_code(self):
        pass
