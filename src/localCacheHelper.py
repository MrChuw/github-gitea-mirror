#!/usr/bin/env python
import json

from loguru import logger

from src.helper import get_config

config = get_config()


def write_local_cache(content):
    try:
        with open(config['local_cache']['path'], 'w') as file:
            file.write(json.dumps(content, indent=4, sort_keys=True))
    except Exception as e:
        logger.error('################# ERROR ####################')
        logger.error('Unable To Save Local Cache !', e)
        logger.error('################# ERROR ####################')


def read_local_cache():
    try:
        with open(config['local_cache']['path'], 'r') as file:
            filedata = file.read()
            return json.loads(filedata)
    except Exception as e:
        logger.error('################# ERROR ####################')
        logger.error('Local Cache File Not Found !  / Unable To Ready It', e)
        logger.error('################# ERROR ####################')

    return dict()


giteaExistsRepos = read_local_cache()
useLocalCache = config['local_cache']['enabled']


def save_local_cache():
    write_local_cache(giteaExistsRepos)
