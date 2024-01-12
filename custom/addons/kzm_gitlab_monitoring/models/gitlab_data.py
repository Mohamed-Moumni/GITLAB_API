import gitlab
from typing import Any
from gitlab import exceptions

class GitlabData:
    """
        This Class contains an interface for gitlab informations for a specific project
    """
    def __init__(self, _username:str, _token:str) -> None:
        self.username = _username
        self.token = _token
    
    def authenticate(self)->None:
        try:
            self.gl = gitlab.Gitlab("https://gitlab.com", private_token=self.token)
            self.gl.auth()
        except exceptions.GitlabAuthenticationError:
            raise ValueError("Invalid Token for Authentication")
    
    def get_project_namespace(self,_url:str):
        is_url = _url.find(".com/")
        if is_url == -1:
            raise ValueError("Invalid Url")
        self.namespace = _url[is_url + 5:]
    
    def get_branch_number(self)->None:
        self.branch_number = len(self.project.branches.list())

    def get_group_name(self)->None:
        self.group = self.project.groups.list()[0].name
    
    def get_project_name(self)->None:
        self.project_name = self.project.name
    
    def get_default_branch(self)->None:
        self.default_branch = self.project.default_branch
    
    def get_last_merge_request(self)->None:
        self.last_merge_request = self.last_merge_request(self.project)
    
    def get_pipeline_status(self)->None:
        self.pipeline_status = self.get_pipeline(self.project)
    
    def get_pipeline(self, project:Any)->str:
        pipeline_list:list = project.pipelines.list()
        if len(pipeline_list) != 0:
            return pipeline_list[0].status
        return "normal"

    def last_merge_request(self, project:Any)->str:
        last_mergerequests_list = project.mergerequests.list(
        state='merged', order_by='updated_at', sort="desc")
        if len(last_mergerequests_list) != 0:
            return last_mergerequests_list[0].title
        return ""

    
    def get_gitlab_infos(self, _url:str)->None:
        try:
            self.authenticate()
            self.get_project_namespace(_url)
            self.project = self.gl.projects.get(self.namespace)
            self.get_branch_number()
            self.get_group_name()
            self.get_project_name()
            self.get_default_branch()
            self.get_last_merge_request()
            self.get_pipeline_status()
        except ValueError as e:
            raise e
        
        
    
    

if __name__ == "__main__":
    gldata = GitlabData("mmoumni", "glpat-2Jdi539E3QAHEqCWtU7_")
    gldata.authenticate()
    gldata.get_gitlab_infos("https://gitlab.com/mmoumni10/gitlab_api")
    for attribute,value in gldata.__dict__.items():
        print(attribute,value)