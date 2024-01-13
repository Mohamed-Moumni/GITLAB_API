import gitlab
from typing import Any
from gitlab import exceptions
import requests


class GitlabData:
    """
        This Class contains an interface for gitlab informations for a specific project
    """

    def __init__(self, _username: str, _token: str) -> None:
        self.username = _username
        self.token = _token

    def authenticate(self) -> None:
        """
            authenticate to gitlab api using private access token
        Raises:
            ValueError: Access token is not valid
        """
        try:
            self.gl = gitlab.Gitlab(
                "https://gitlab.com", private_token=self.token)
            self.gl.auth()
        except exceptions.GitlabAuthenticationError:
            raise ValueError("Invalid Token for Authentication")

    def get_project_namespace(self, _url: str):
        """
            grab the project namespace from the url
            for example: https://gitlab.com/group_name/project_name
            this method will set /group_name/project_name as project namespace

        Args:
            _url (str): url of the project

        Raises:
            ValueError: Invalid Error
        """
        is_url = _url.find(".com/")
        if is_url == -1:
            raise ValueError("Invalid Url")
        self.namespace = _url[is_url + 5:]

    def get_branch_number(self) -> None:
        self.branch_number = len(self.project.branches.list())

    def get_group_name(self) -> None:
        self.group = self.project.groups.list()[0].name

    def get_project_name(self) -> None:
        self.project_id = self.project.id
        self.project_name = self.project.name

    def get_default_branch(self) -> None:
        self.default_branch = self.project.default_branch
        self.default_branch_id = self.project.branches.get(self.default_branch)

    def get_last_merge_request(self) -> None:
        self.last_merge_request = self.last_merge_request(self.project)

    def get_pipeline_status(self) -> None:
        self.pipeline_status = self.get_pipeline(self.project)

    def get_access_token_name(self) -> None:
        self.access_token_name = self.gl.personal_access_tokens.get(
            "self").name

    def get_expiration_date(self) -> None:
        self.expiration_date = self.gl.personal_access_tokens.get(
            "self").expires_at

    def get_gitlab_members(self) -> list[str]:
        return self.project.members_all.list(get_all=True)

    def get_pipeline(self, project: Any) -> str:
        """
            get the pipeline status of the last commit of the default branch

        Args:
            project (Any): project object from gitlab

        Returns:
            str: success,failed or normal
        """
        pipeline_list: list = project.pipelines.list()
        if len(pipeline_list) != 0:
            return pipeline_list[0].status
        return "normal"

    def last_merge_request(self, project: Any) -> str:
        """
            get The last merge Request

        Args:
            project (Any): project object from gitlab

        Returns:
            str: last_merge_request commit name
        """
        last_mergerequests_list = project.mergerequests.list(
            state='merged', order_by='updated_at', sort="desc")
        if len(last_mergerequests_list) != 0:
            return last_mergerequests_list[0].title
        return ""

    def get_quality_code(self) -> float:
        """
            get the quality code of the last commit of the default branch

        Returns:
            float: quality code in float format
        """
        pipelines = self.project.pipelines.list()
        pipeline_job = pipelines[0].jobs.list()
        job_id = pipeline_job[0].id
        url = "https://gitlab.com/api/v4/projects/" + \
            str(self.project_id) + "/jobs/" + str(job_id) + "/trace"
        headers = {'PRIVATE-TOKEN': self.token}
        trace = requests.get(url, headers=headers).text
        start = trace.find("Your code has been rated at")
        end = trace[start:].find("\n")
        quality_code = trace[start:start + end]
        quality_code = float(quality_code.split()[6].split('/')[0])
        return quality_code

    def get_gitlab_infos(self, _url: str) -> None:
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
            self.get_access_token_name()
            self.get_expiration_date()
        except ValueError as e:
            raise e
