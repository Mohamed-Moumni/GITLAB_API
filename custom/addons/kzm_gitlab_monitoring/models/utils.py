import gitlab
from typing import Dict


def gitlab_authenticate(_url: str, _private_token: str):
    """_summary_

    Args:
        _url (str): _description_
        _private_token (str): _description_

    Returns:
        _type_: _description_
    """
    gl = gitlab.Gitlab(url=_url, private_token=_private_token)
    gl.auth()
    return gl


def get_project_namespace(_url: str) -> str:
    """ parse the url and get the namespace of the project

    Args:
        _url (str): url provided by the git_link

    Raises:
        ValueError: Invalid Url Error

    Returns:
        str: return the namespace of the project specified in the url
    """
    is_url = _url.find(".com/")
    if is_url == -1:
        raise ValueError("Invalid Url")
    return _url[is_url + 5:]

def get_pipeline(project)->str:
    pipeline_list:list = project.pipelines.list()
    if len(pipeline_list) != 0:
        return pipeline_list[0].status
    return "normal"
        

def get_gitlab_infos(project_link: str, token: str) -> Dict[str, str]:
    """_summary_

    Args:
        project_link (str): _description_
        token (str): _description_

    Returns:
        Dict[str, str]: _description_
    """
    gitlab_infos: Dict[str, str] = {}

    gl = gitlab_authenticate("https://gitlab.com", token)
    namespace = get_project_namespace(project_link)
    project = gl.projects.get(namespace)
    gitlab_infos['group'] = project.groups.list()[0].name
    last_mergerequests_list = project.mergerequests.list(
        state='merged', order_by='updated_at', sort="desc")
    if len(last_mergerequests_list) != 0:
        gitlab_infos['last_merge_request'] = last_mergerequests_list[0]
    else:
        gitlab_infos['last_merge_request'] = ""
    gitlab_infos['default_branch'] = project.default_branch
    gitlab_infos['branch_number'] = len(project.branches.list())
    gitlab_infos['project_name'] = project.name
    gitlab_infos['pipeline_status'] = get_pipeline(project)
    return gitlab_infos
