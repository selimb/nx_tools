"""
    nx_tools.utils
    ~~~~~~~~~~~~~~

    Utility functions.
"""
import collections
import json
import logging
import os
from pprint import pformat

from .constants import DEFAULT_CONFIG_PATH, USER_CONFIG_PATH
from .exceptions import UserConfigNotFound


logger = logging.getLogger(__name__)


def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug('Ensured %s exists.' % directory)


def get_filename(f):
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    return filename
