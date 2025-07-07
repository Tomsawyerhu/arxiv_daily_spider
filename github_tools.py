import os
import subprocess
import time


def read_token(token_file):
    with open(token_file, 'r') as f:
        github_token = f.read()
        return github_token


def run_command(command, cwd=None):
    if cwd is None:
        extra_args = {}
    else:
        extra_args = {
            'cwd': cwd
        }
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            **extra_args
        )
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            'stdout': e.stdout,
            'stderr': e.stderr,
            'returncode': e.returncode,
            'error': str(e)
        }


def github_login(token_file):
    command = f'gh auth login --with-token < {token_file}'
    result = run_command(command)
    if result['stderr'] and result['returncode'] != 0:
        print("登录失败, 失败报错: %s" % result['stderr'])
        return False
    else:
        print('登录成功')
        return True


def clone_repo_to_local(local_repo_dir, github_user, remote_repo):
    if os.path.exists(local_repo_dir):
        print(f"{local_repo_dir} already exist")
    else:
        github_url = 'https://github.com/{}/{}.git'.format(github_user, remote_repo)
        git_clone_cmd = 'git clone %s' % github_url
        git_clone_result = run_command(git_clone_cmd, cwd=os.path.dirname(local_repo_dir))
        print(git_clone_result)


def add_commit_and_push(github_token, github_user, local_repo_dir, remote_repo, remote_branch):
    # 3. 提交到github
    git_add_command = 'git add .'
    git_commit_command = 'git commit -m "daily update"'
    git_push_command = f'git push https://{github_token}@github.com/{github_user}/{remote_repo}.git {remote_branch}'
    add_result = run_command(git_add_command, cwd=local_repo_dir)
    print(add_result)
    commit_result = run_command(git_commit_command, cwd=local_repo_dir)
    print(commit_result)
    push_result = run_command(git_push_command, cwd=local_repo_dir)
    print(push_result)
    if push_result['returncode'] != 0:
        print('initialize push fail, error %s' % push_result['stderr'])
    else:
        print('initialize push success')


def is_git_global_config_exist():
    git_config_list = 'git config --list'
    git_config_str = run_command(git_config_list)['stdout']
    is_config_exist = 'user.email' in git_config_str and 'user.name' in git_config_str
    return is_config_exist


def set_git_global_config(github_user, github_email):
    set_name_config = f'git config --global user.name "{github_user}"'
    set_email_config = f'git config --global user.email "{github_email}"'
    run_command(set_name_config)
    result = run_command(set_email_config)
    return result
