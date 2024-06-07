#!/usr/bin/env python
# https://github.com/PyGithub/PyGithub
import time

from github import GithubException
from loguru import logger

from src.helper import (
    get_config, gh_api, gitea_create_repo, gitea_create_user_or_org, gitea_get_user, gitea_set_repo_topics,
    is_blacklisted_repository,
)
from src.localCacheHelper import giteaExistsRepos, save_local_cache


def repository_forked():
    config = get_config()
    repo_map = config['repo_map']
    gh = gh_api()
    loop_count = 0

    for repo in gh.get_user().get_repos():
        if repo.fork:
            loop_count = loop_count + 1
            real_repo = repo.full_name.split('/')[1]
            gitea_dest_user = repo.owner.login
            repo_owner = repo.owner.login

            logger.info('Forked Repository : {0}'.format(repo.full_name))

            if is_blacklisted_repository(repo.full_name):
                logger.warning("        ---> Warning : Repository Matches Blacklist")
                continue

            if real_repo in repo_map:
                gitea_dest_user = repo_map[real_repo]

            gitea_uid = gitea_get_user(gitea_dest_user)

            if gitea_uid == 'failed':
                gitea_uid = gitea_create_user_or_org(gitea_dest_user, repo.owner.type)

            repo_name = "{0}".format(real_repo)

            m = {"repo_name": repo_name, "description": (repo.description or "not really known")[:255],
                 "clone_addr": repo.clone_url, "mirror": True, "private": repo.private, "uid": gitea_uid,
                 }

            status = gitea_create_repo(m, repo.private, True)

            if status == 'exists' and f"{repo.owner.login}/{repo.id}" not in giteaExistsRepos:
                giteaExistsRepos[f"{repo.owner.login}/{repo_name}"] = f"{gitea_dest_user}/{repo_name}"

            if status != 'failed':
                try:
                    if status != 'exists':
                        giteaExistsRepos[f"{repo.owner.login}/{repo_name}"] = f"{gitea_dest_user}/{repo_name}"
                        topics = repo.get_topics()
                        topics.append('forked-repo')
                        topics.append('forked-{0}-repo'.format(repo_owner))
                        gitea_set_repo_topics(repo_owner, repo_name, topics)
                except GithubException as e:
                    logger.error("###[error] ---> Github API Error Occurred !")
                    logger.error(e)
                    logger.error("###[error] ---> Github API Error Occurred !")
            else:
                logger.info(repo)

            if loop_count % 50 == 0:
                logger.warning('################# WARNING ####################')
                logger.warning('Time To Sleep For 5 Seconds')
                logger.warning('################# WARNING ####################')
                time.sleep(5)
            else:
                logger.info("\n\r")
    save_local_cache()
