from github_tools import *
from spider import *
from markdown import *

if __name__ == '__main__':
    token_file = f'{ROOT}/config/token.txt'
    github_token = read_token(token_file)
    local_repo = f"{ROOT}/EveryDaySeArxiv"
    remote_repo = 'EveryDaySeArxiv'
    github_user = 'Tomsawyerhu'
    github_email = '1095549886@qq.com'

    if not is_git_global_config_exist():
        set_git_global_config(github_user,github_email)

    download_latest_arxiv_papers()
    transform_arxiv_paper_to_json()

    github_login(token_file)
    if not os.path.exists(local_repo):
        clone_repo_to_local(local_repo, github_user, remote_repo)

    os.system(f'cp -rf {ROOT}/markdown/* {local_repo}')
    add_commit_and_push(github_token, github_user, local_repo, remote_repo, remote_branch='master')
