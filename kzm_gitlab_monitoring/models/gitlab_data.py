from typing import Any, List
from gitlab import exceptions
import gitlab
import requests
from urllib.parse import urlparse

GITLAB = "https://gitlab.com/"
GITALB_API_PROJECT = "https://gitlab.com/api/v4/projects/"


class GitlabData:
    """
        This Class contains an interface for gitlab informations for a specific project
    """

    def __init__(self, _token: str) -> None:
        """
            GitlabData Constructor

        Args:
            _token (str): gitlab access_token

        Raises:
            ValueError: raised when Invalid Token for Authentication is given
        """
        try:
            self.gl = gitlab.Gitlab(GITLAB, private_token=_token)
            self.gl.auth()
            self.token = _token
            self.access_token_name = self.gl.personal_access_tokens.get(
                "self").name
            self.expiration_date = self.gl.personal_access_tokens.get(
                "self").expires_at
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
        url = urlparse(_url)
        if url and url.path:
            namespace = url.path.strip('/')
            self.namespace = namespace.replace('.git', '')
        else:
            raise ValueError("Invalid Url")

    def get_project(self) -> None:
        """
            get the gitlab project instance
        """
        self.project = self.gl.projects.get(self.namespace)

    def get_branch_number(self) -> None:
        """
            get the number of branch in gitlab project
        """
        self.branch_number = len(self.project.branches.list(get_all=True))

    def get_group_name(self) -> None:
        """
            get the name of the group for the project
        """
        self.group = self.project.groups.list(get_all=True)[0].name

    def get_project_name(self) -> None:
        """
            get the gitlab project name 
        """
        self.project_id = self.project.id
        self.project_name = self.project.name

    def get_default_branch(self) -> None:
        """
            get the gitlab default branch
        """
        self.default_branch = self.project.default_branch
        self.default_branch_id = self.project.branches.get(self.default_branch)

    def get_last_merge_request(self) -> None:
        """
            get the last merge request in the project
        """
        self.last_merge_request = self.last_merge_request(self.project)

    def get_pipeline_status(self) -> None:
        """
            get the pipeline status
        """
        self.pipeline_status = self.get_pipeline(self.project)

    def get_gitlab_members(self) -> List[str]:
        """
            get gitlab members list
        Returns:
            List[str]: _description_
        """
        return self.project.members_all.list(get_all=True)

    def get_pipeline(self, project: Any) -> str:
        """
            get the pipeline status of the last commit of the default branch

        Args:
            project (Any): project object from gitlab

        Returns:
            str: success,failed or normal
        """
        pipeline_list: list = project.pipelines.list(get_all=True)
        if len(pipeline_list) != 0:
            self.pipeline_id = pipeline_list[0].id
            return pipeline_list[0].status
        self.pipeline_id = None
        return "undefined"

    def last_merge_request(self, project: Any) -> str:
        """
            get The last merge Request

        Args:
            project (Any): project object from gitlab

        Returns:
            str: last_merge_request commit name
        """
        last_mergerequests_list = project.mergerequests.list(
            state='merged', order_by='updated_at', sort="desc", get_all=True)
        if len(last_mergerequests_list) != 0:
            return last_mergerequests_list[0].title
        return ""

    def get_quality_code(self) -> float:
        """
            calculate the quality code via the logs of the first job in the last pipeline

        Raises:
            ValueError: Job_id not Found
            ValueError: Project Pipeline jobs not Founds

        Returns:
            float: quality Code value
        """
        _url = GITALB_API_PROJECT + \
            str(self.project_id) + "/pipelines/" + \
            str(self.pipeline_id) + "/jobs/"
        headers = {'Private-Token': self.token}
        params = {'ref': self.default_branch}
        response = requests.get(url=_url, headers=headers, params=params)

        if response.status_code == 200:
            jobs = response.json()
            job_id = jobs[len(jobs) - 1]['id']
            _url = GITALB_API_PROJECT + \
                str(self.project_id) + "/jobs/" + str(job_id) + "/trace"

            res = requests.get(url=_url, headers=headers)

            if res.status_code == 200:
                trace = res.text
                start = trace.find("Your code has been rated at")
                if (start == -1):
                    return 0.0
                end = trace[start:].find("\n")
                quality_code = trace[start:start + end]
                quality_code = float(quality_code.split()[6].split('/')[0])
            else:
                raise ValueError("Job_id not Found")
        else:
            raise ValueError("Project Pipeline jobs not Founds")
        return quality_code

    def get_gitlab_infos(self, _url: str) -> None:
        """


        Args:
            _url (str): Url of the project

        Raises:
            ValueError: Error while getting the Gitlab infos
        """
        try:
            self.get_project_namespace(_url)
            self.get_project()
            self.get_branch_number()
            self.get_group_name()
            self.get_project_name()
            self.get_default_branch()
            self.get_last_merge_request()
            self.get_pipeline_status()
        except ValueError as e:
            raise ValueError(f"Gitlab Infos Error: {e}")
