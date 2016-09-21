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


def ensure_dir_exists(directory):
    """Create directory if it does not already exist."""
    logger = logging.getLogger(__name__)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info("Directory created: %s" % directory)


def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def write_json(obj, filepath):
    ensure_dir_exists(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(obj, f, separators=(',', ':'), indent=4)


def recursive_dict_update(d, u):
    """Recursively update `d` from `u`."""
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def read_default_config():
    try:
        return load_json(DEFAULT_CONFIG_PATH)
    except IOError:
        raise AssertionError("Could not find default config at %s "
                             % DEFAULT_CONFIG_PATH)


def read_user_config():
    try:
        return load_json(USER_CONFIG_PATH)
    except IOError:
        raise UserConfigNotFound("Could not find user config at %s "
                                 % USER_CONFIG_PATH)
    except ValueError:
        raise UserConfigNotFound("Not a JSON object")


def read_config():
    """User takes precedence over default."""
    logger = logging.getLogger(__name__)
    default = read_default_config()
    try:
        user = read_user_config()
        logger.debug("User config:\n%s" % pformat(user))
    except UserConfigNotFound as e:
        user = {}
        logger.debug("User Config ignored: %s" % e)
    config = recursive_dict_update(default, user)
    logger.debug("Result config:\n%s" % pformat(config))
    return config


def is_exe(value):
    if value[-4:] == '.exe':
        return True
    else:
        return False


def get_patch_loc(config, nx_version, key):
    d = config[key]['patch']
    try:
        return d[nx_version]
    except KeyError:
        try:
            return d[nx_version[:4]]
        except KeyError:
            raise ConfigError("%s patch directory not found for %s."
                    % (key, nx_version))

def get_build_loc(config, nx_version, key):
    d = config[key]['build']
    try:
        return d[nx_version]
    except KeyError:
        raise ConfigError("%s build directory not found for %s."
                % (key, nx_version))


def is_frozen_build(nx_version, config):
    logger = logging.getLogger(__name__)
    if nx_version not in config['remote']['build']:
        logger.debug("No remote found for this version.")
        return True
    if utils.is_exe(config['local']['build'][nx_version]):
        logger.debug("Frozen build: executable")
        return True
    return False
