import os
import sys

from loguru import logger

from src.gistsSource import gists_source
from src.gistsStared import gists_stared
from src.helper import get_config
from src.repositoryForked import repository_forked
from src.repositorySource import repositorySource
from src.repositoryStared import repositoryStared


def main():
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(1, "{0}/src/".format(THIS_FOLDER))

    config = get_config()

    if config['gistsSource']:
        logger.info('Setting Up Mirror For Source Github Gists')
        gists_source()
        logger.info('Finished\n\r')

    if config['gistsStared']:
        logger.info('Setting Up Mirror For Stared Github Gists')
        gists_stared()
        logger.info('Finished\n\r')

    if config['repositoryForked']:
        logger.info('Setting Up Mirror For Forked Github Repository')
        repository_forked()
        logger.info('Finished\n\r')

    if config['repositorySource']:
        logger.info('Setting Up Mirror For Source Github Repository')
        repositorySource()
        logger.info('Finished\n\r')

    if config['repositoryStared']:
        logger.info('Setting Up Mirror For Stared Github Repository')
        repositoryStared()
        logger.info('Finished\n\r')
