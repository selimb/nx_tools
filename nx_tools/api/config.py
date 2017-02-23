import json
import logging
import shutil
import subprocess

from .constants import DEFAULT_CONFIG_PATH, USER_CONFIG_PATH, NPP
from .exceptions import UserConfigNotFound, UserConfigInvalid
from . import utils


logger = logging.getLogger(__name__)

_BACKUP_EXT = '.bak'
TMG_KEY = 'tmg'
NX_KEY = 'nx'


def read_config():
    return Config(_read_config())


class Config(object):
    '''Simple wrapper around a dictionary'''
    def __init__(self, dct):
        self._conf = dct

    def get(self, key):
        try:
            return self._conf[key]
        except KeyError:
            raise AssertionError('Configuration has no %s entry' % key)

    def local_TMG_dir(self, nx_version):
        raise NotImplementedError

    def remote_TMG_dir(self, nx_version):
        raise NotImplementedError

    def local_NX_dir(self, nx_version):
        raise NotImplementedError

    def remote_NX_dir(self, nx_version):
        raise NotImplementedError

    def _local_dir(self, item_type, nx_version):
        raise NotImplementedError

    def _fuzzy_version(nx_version, available):
        '''Matches `nx_version` given pool of `available` versions.

        For example, if `nx_version` is "nx1003" and "nx10" is available,
        "nx10" is returned.
        '''
        if nx_version in available:
            return nx_version

        matches = []
        for v in available:
            n = len(v)
            if v == nx_version[:v]:
                matches.append(v)

        if not matches:
            msg = 'No match for %s in %s' % (nx_version, available)
            raise UserConfigInvalid(msg)

        if len(matches) > 1:
            raise UserConfigInvalid(
                'Ambiguous. Found %i matches for %s in %s: %s'
                % (len(matches), nx_version, available, matches)
            )

        return matches[0]

    def _tracked_tmg(self):
        raise NotImplementedError

    def _tracked_nx(self):
        raise NotImplementedError


def _read_config():
    default = read_default_config()
    try:
        user = read_user_config()
        logger.debug('User config:\n' + pformat(user))
    except UserConfigNotFound as e:
        user = {}
        logger.debug(e.message)
    conf = recursive_dict_update(default, user)
    logger.debug('Result config:\n' + pformat(config))
    return conf


def _read_default_config():
    try:
        return load_json(DEFAULT_CONFIG_PATH)
    except IOError:
        msg = 'Could not find default config at %s ' % DEFAULT_CONFIG_PATH
        raise AssertionError(msg)


def _read_user_config():
    try:
        return load_json(USER_CONFIG_PATH)
    except IOError:
        msg = 'Could not find user config at %s ' % USER_CONFIG_PATH
        raise UserConfigNotFound(msg)
    except ValueError as e:
        raise UserConfigInvalid('User config not a valid JSON object\n' + e.message)


def _split_duplicates(location_dict):
    err_msg = 'Multiple definitions for %s.'
    r = {}
    sep = ','
    for key in location_dict:
        val = location_dict[key]
        if not sep in key:
            if key in r:
                raise UserConfigInvalid(err_msg % key)
            r[key] = val
            continue
        new_keys = key.split(sep)
        for new_key in new_keys:
            if new_key in r:
                raise UserConfigInvalid(err_msg % key)
            r[new_key] = val
    return r

def _recursive_dict_update(d, u):
    '''Recursively update `d` from `u`.'''
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def _load_json(filepath):
    s = open(filepath).read().replace('\\', '\\\\')
    return json.loads(s)


def _write_json(obj, filepath):
    utils.ensure_dir_exists(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(obj, f, separators=(',', ':'), indent=4)

