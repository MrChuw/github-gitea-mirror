#!/usr/bin/env python
# https://github.com/PyGithub/PyGithub
import fnmatch
import json
import os

import requests
from github import Github
from loguru import logger

giteaGetUserCache = dict()
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
config = json.loads(open(os.path.expanduser(f"{THIS_FOLDER}/config.json")).read().strip())


def get_config():
    return config


def gitea_host(end_point):
    return "{0}/api/v1/{1}".format(config['gitea']['host'], end_point)


def gh_api():
    return Github(config['github']['access-token'])


def gitea_session():
    access_token = config['gitea']['access-token']
    request_session = requests.Session()
    request_session.headers.update({"Content-type": "application/json", "Authorization": f"token {access_token}"})

    return request_session


session = gitea_session()


def gitea_set_repo_topics(owner, repo_name, topics):
    m = {"topics": topics,
         }

    r = session.put(gitea_host(f"repos/{owner}/{repo_name}/topics"), data=json.dumps(m))

    if r.status_code == 204:
        logger.info('        ---> Success : Repository Topics Set')
    else:
        logger.error('        ---> Error : Unable To SetRepository Topics')
        logger.error(r.text, json.dumps(m))


def gitea_set_repo_star(owner, repo_name):
    r = session.put(gitea_host(f"user/starred/{owner}/{repo_name}/"))

    if r.status_code == 204:
        logger.info('        ---> Success : Repository Starred')
    else:
        logger.error('        ---> Error : Unable To Star The Repository')


def gitea_create_repo(data, is_private, is_repository):
    if is_private:
        data["auth_username"] = config['github']['username']
        data["auth_password"] = config['github']['access-token']

    if is_repository:
        data["service"] = 'github'
        data["wiki"] = True
        data["auth_token"] = config['github']['access-token']

    json_string = json.dumps(data)
    response = session.post(gitea_host('repos/migrate'), data=json_string)

    if response.status_code == 201:
        logger.info("        ---> Success : Repository Created")
        return 'created'
    elif response.status_code == 409:
        logger.warning("        ---> Warning : Repository Already Exists")
        return 'exists'
    else:
        logger.error(str(response.status_code), response.text, json_string, "\n\r")
        return 'failed'


def gitea_create_org(org_name):
    body = {'full_name': org_name, 'username': org_name,
            }

    json_string = json.dumps(body)
    r = session.post(gitea_host('orgs/'), data=json_string)

    if r.status_code != 201:
        return 'failed'

    giteaGetUserCache[f"{org_name}"] = json.loads(r.text)["id"]
    return giteaGetUserCache[org_name]


def gitea_create_user(org_name):
    body = {'email': f"{org_name}@gitea.dev", 'full_name': org_name, 'login_name': org_name, 'username': org_name,
            'password': config['gitea']['default_user_password'],
            }

    json_string = json.dumps(body)
    r = session.post(gitea_host('admin/users'), data=json_string)

    if r.status_code != 201:
        return 'failed'

    giteaGetUserCache[f"{org_name}"] = json.loads(r.text)["id"]
    return giteaGetUserCache[org_name]


def gitea_create_user_or_org(name, user_org):
    if user_org == 'User':
        return gitea_create_user(name)

    return gitea_create_org(name)


def gitea_get_user(username):
    if username in giteaGetUserCache:
        return giteaGetUserCache[username]

    r = session.get(gitea_host(f'users/{username}'))
    if r.status_code != 200:
        return 'failed'
    giteaGetUserCache["{0}".format(username)] = json.loads(r.text)["id"]
    return giteaGetUserCache[username]


def gitea_get_user_repos(user_uid):
    loop_count = 1
    results = dict()

    while loop_count != 0:
        r = session.get(gitea_host(f'repos/search?uid={user_uid}&page={loop_count}&limit=50'))

        if r.status_code != 200:
            break

        data = json.loads(r.text)

        if data['ok']:
            if len(data['data']) == 0:
                break
            else:
                if len(results) == 0:
                    results = data['data']
                else:
                    results = results + data['data']

        loop_count += 1

    return results


def gitea_get_all_users_orgs(users_orgs):
    loop_count = 1
    results = dict()

    if users_orgs == 'users':
        users_orgs = 'admin/users'
    else:
        users_orgs = 'orgs'

    while loop_count != 0:
        r = session.get(gitea_host(f'{users_orgs}?page={loop_count}&limit=50'))

        if r.status_code != 200:
            break

        data = json.loads(r.text)

        if len(data) == 0:
            break
        else:
            if len(results) == 0:
                results = data
            else:
                results = results + data

        loop_count += 1

    return results


def is_blacklisted_repository(full_name):
    blacklist = config.get('blacklist', [])
    if isinstance(blacklist, str):
        blacklist = [blacklist]

    for pattern in blacklist:
        if fnmatch.fnmatch(full_name, pattern):
            return True
    return False
