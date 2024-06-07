#!/usr/bin/env python
# https://github.com/PyGithub/PyGithub
from github import GithubException
from loguru import logger

from .helper import (
    get_config, gh_api, gitea_create_org, gitea_create_repo, gitea_create_user_or_org, gitea_get_user, gitea_set_repo_topics,
)
from .localCacheHelper import giteaExistsRepos, save_local_cache


def gists_source():
    config = get_config()
    gh = gh_api()

    default_gist_user = gitea_get_user('gist')
    if default_gist_user == 'failed':
        default_gist_user = gitea_create_org('gist')

    for repo in gh.get_user().get_gists():
        if repo.public:
            is_private = False
        else:
            is_private = True

        logger.info(f'Gist : {repo.owner.login}/{repo.id}')

        prefix = ''
        suffix = ''
        gitea_uid = gitea_get_user(repo.owner.login)
        repo_owner = repo.owner.login

        if gitea_uid == 'failed':
            gitea_uid = gitea_create_user_or_org(repo.owner.login, repo.owner.type)

        if gitea_uid == 'failed':
            gitea_uid = default_gist_user
            repo_owner = 'gist'

        gist_prefix = config['gitea']['gist']['prefix']
        gist_suffix = config['gitea']['gist']['suffix']
        if len(gist_prefix) != 0:
            prefix = f"{gist_prefix}-"

        if len(gist_suffix) != 0:
            suffix = f"-{gist_suffix}"

        m = {"repo_name": f"{prefix}{repo.id}{suffix}", "description": (repo.description or "not really known")[:255],
             "clone_addr": repo.git_pull_url, "mirror": True, "private": is_private, "uid": gitea_uid,
             }

        status = gitea_create_repo(m, is_private, False)

        if status == 'exists' and f"{repo.owner.login}/{repo.id}" not in giteaExistsRepos:
            giteaExistsRepos[f"{repo.owner.login}/{repo.id}"] = f"{repo_owner}/{m['repo_name']}"

        if status != 'failed':
            try:
                if status != 'exists':
                    giteaExistsRepos[f"{repo.owner.login}/{repo.id}"] = f"{repo_owner}/{m['repo_name']}"
                    topics = ['gist', f'{repo_owner}-gist']
                    if is_private:
                        topics.append('secret-gist')
                        topics.append(f'secret-{repo_owner}-gist')
                    else:
                        topics.append('public-gist')
                        topics.append(f'public-{repo_owner}-gist')
                    gitea_set_repo_topics(repo_owner, m["repo_name"], topics)
            except GithubException as e:
                logger.error("###[error] ---> Github API Error Occurred !")
                logger.error(e)
                logger.error("###[error] ---> Github API Error Occurred !")

        if status == 'failed':
            logger.error(repo)

        logger.info("\n\r")
    save_local_cache()
