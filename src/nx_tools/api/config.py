# TODO: Move this somewhere else (README?)
'''
Glossary
--------
nx_tools purposefully uses Git-like terms. Those guys came up with beautiful
abstractions and I certainly couldn't do any better.

Project: NX and TMG are the only two supported projects.
NX version: Both the NX and TMG projects have their releases tied to different
    NX versions, e.g. NX11.
Branch: A branch simply consists of a local and a remote location. Branches are
    uniquely identified by a Project and an NX version.
Location: Either a directory or an executable (see frozen branches).
Frozen branch: A branch where the remote location is never updated. This is inferred
    from the fact that the remote location is an executable.
    Only applicable to the NX project.
Tracked branch: A branch where both a local and remote location are specified.
Untracked branch: A branch where only the local location is specified.
'''
import collections
import functools
import json
import logging
import os
from pprint import pformat
import shutil
import subprocess

from . import utils
from .constants import DEFAULT_CONFIG_PATH, USER_CONFIG_PATH
from .exceptions import UserConfigInvalid, UserConfigNotFound

logger = logging.getLogger(__name__)

_BACKUP_EXT = '.bak'
TMG_KEY = 'tmg'
NX_KEY = 'nx'


def read_config():
    return Config(_read_config())


class Config(object):
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

    def _tracked_tmg(self):
        raise NotImplementedError

    def _tracked_nx(self):
        raise NotImplementedError


def _read_combined_config(user_config_path):
    default = _read_default_config()
    default_parsed = _parse_config(default)
    try:
        user = _read_user_config(user_config_path)
        logger.debug('User config:\n' + pformat(user))
    except UserConfigNotFound as e:
        user = {}
        logger.debug(e.message)
    combined = recursive_dict_update(default, user)
    logger.debug('Result config:\n' + pformat(config))
    return combined


def _read_default_config():
    try:
        return _load_json(DEFAULT_CONFIG_PATH)
    except IOError:
        msg = 'Could not find default config at %s ' % DEFAULT_CONFIG_PATH
        raise AssertionError(msg)


def _read_user_config(fpath):
    try:
        return _load_json(fpath)
    except IOError:
        msg = 'Could not find user config at %s ' % fpath
        raise UserConfigNotFound(msg)
    except ValueError as e:
        raise UserConfigInvalid('User config not a valid JSON object\n' + e.message)


def _fuzzy_version(nx_version, available):
    '''Matches `nx_version` given pool of `available` versions.

    For example, returns 'nx10' if `nx_version` is 'nx1003'
    and 'nx10' is available, but returns 'nx1003' if 'nx1003' and 'nx10'
    are available.
    '''
    if nx_version in available:
        return nx_version

    matches = []
    for v in available:
        n = len(v)
        if v == nx_version[:n]:
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


def _parse_config(dct):
    '''Empties input dictionary'''
    user_vars = _pop_vars(dct)
    r = {}
    for project_key in (TMG_KEY, NX_KEY):
        try:
            project = dct.pop(project_key)
        except KeyError:
            raise AssertionError('Missing project key %s' % project_key)
        r[project_key] = _expand_project(project, user_vars)
    for key in dct.keys():
        r[key] = dct.pop(key)
    return r


def _expand_project(proj_dict, user_vars):
    rule_key = 'target_rule'
    miss_var = 'Undefined variable %s in %s branch: %r'
    r = {}
    vrs = user_vars.copy()
    try:
        rule = proj_dict[rule_key]
    except KeyError:
        rule = None

    for key in proj_dict.keys():
        if key == rule_key:
            continue

        branch = proj_dict[key]
        remote = branch[0]
        try:
            local = branch[1]
        except IndexError:
            local = None

        if remote is not None:
            try:
                remote = _expand(remote, user_vars)
            except KeyError as e:
                raise UserConfigInvalid(miss_var % (e.message, key, branch))

        if _is_frozen_remote(remote):
            local = None
            r[key] = [remote, local]
            continue


        if local is None:
            if not rule:
                raise UserConfigInvalid('Must use a "target_rule". %r' % branch)
            local = rule

        vrs.update({'version': key})
        try:
            local = _expand(local, vrs)
        except KeyError as e:
            raise UserConfigInvalid(miss_var % (e.message, key, branch))
        r[key] = [remote, local]
    return r


def _is_frozen_remote(remote):
    if remote[-4:] == '.exe':
        return True
    return False


def _expand(s, user_vars):
    return s.format(**user_vars)


def _pop_vars(dct):
    user_vars = {}
    for key in dct.keys():
        if key == key.upper():
            user_vars[key] = dct.pop(key)
    return user_vars


def _recursive_dict_update(d, u):
    '''Recursively update `d` from `u`.'''
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = _recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def _load_json(filepath):
    s = open(filepath).read().replace('\\', '\\\\')
    minified = ''
    for line in s.split('\n'):
        if line.strip().startswith('//'):
            continue
        minified += line + '\n'
    return json.loads(minified)


def _write_json(obj, filepath):
    utils.ensure_dir_exists(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(obj, f, separators=(',', ':'), indent=4)
