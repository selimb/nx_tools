# TODO: Move this somewhere else (README?)
# TODO: Mention that {version} cannot be used in remotes
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
    from the fact that the remote location is an executable. The local location
    is irrelevant in this case.
    Only applicable to the NX project.
Untracked branch: A branch where only the local location is specified.
Tracked branch: A branch where both a local and remote location are specified.
'''
import collections
import functools
import logging
import os
from pprint import pformat
import shutil
import subprocess

from . import utils
from .exceptions import InvalidConfig, NXToolsError

logger = logging.getLogger(__name__)

TRACKED = 'tracked'
FROZEN = 'frozen'
LOCAL = 'local'

_TMG_KEY = 'tmg'
_NX_KEY = 'nx'

Branch = collections.namedtuple('Branch', ('remote', 'local', 'stat'))


class Environment(object):

    project_keys = (_TMG_KEY, _NX_KEY)

    def __init__(self, *fpaths_json):
        if len(fpaths_json) == 0:
            raise NXToolsError('Must supply at least one path')
        dct = None
        for fpath in fpaths_json:
            logger.debug('Loading JSON config from %s' % fpath)
            try:
                new = utils.load_json(fpath)
            except IOError:
                raise ConfigNotFound(fpath)
            except ValueError as e:
                msg = 'Invalid configuration %s\n%s' % (fpath, e.message)
                raise InvalidConfig(msg)
            if not dct:
                dct = new
                continue
            logger.debug('Updating existing JSON with:\n%s' % pformat(new))
            dct = _recursive_dict_update(dct, new)
            logger.debug('Result JSON:\n%s' % pformat(dct))

        self._conf = _parse(dct)
        logger.debug('Parsed configuration:\n%s' % pformat(self._conf))

    @classmethod
    def from_json(cls, *fpaths_json):
        return cls(conf)

    def get_option(self, key):
        if key in self.project_keys:
            raise NXToolsError('Use helper functions instead.')
        try:
            return self._conf[key]
        except KeyError:
            raise NXToolsError('Configuration has no %s entry' % key)

    def get_tmg_branch(self, nx_version):
        return self._mk_branch(_TMG_KEY, nx_version, True)

    def get_nx_branch(self, nx_version):
        return self._mk_branch(_NX_KEY, nx_version, False)

    def list_tmg_versions(self):
        return self._list_versions(_TMG_KEY)

    def list_nx_versions(self):
        return self._list_versions(_NX_KEY)

    def _list_versions(self, project_key):
        return self._conf[project_key].keys()

    def _mk_branch(self, project_key, nx_version, fuzzy):
        project = self._conf[project_key]
        available = project.keys()
        ver = nx_version
        if fuzzy:
            ver = self._fuzzy_version(ver, available)

        if not ver in available:
            msg = ('Could not find %s branch with version %s\n' % (project, ver))
            msg += 'Available: ' + ' '.join(available)
            raise NXToolsError(msg)

        remote, local = project[ver]
        stat = TRACKED
        if local is None:
            stat = FROZEN
        elif remote is None:
            stat = LOCAL

        return Branch(local=local, remote=remote, stat=stat)

    @staticmethod
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
            raise NXToolsError(msg)

        if len(matches) > 1:
            raise NXToolsError(
                'Ambiguous. Found %i matches for %s in %s: %s'
                % (len(matches), nx_version, available, matches)
            )

        return matches[0]


def _parse(json_dict):
    dct = json_dict.copy()
    user_vars = _pop_vars(dct)
    r = {}
    for project_key in (_TMG_KEY, _NX_KEY):
        try:
            project = dct.pop(project_key)
        except KeyError:
            raise InvalidConfig('Missing project key %s' % project_key)
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
                raise InvalidConfig(miss_var % (e.message, key, branch))

            if _is_frozen_remote(remote):
                local = None
                r[key] = [remote, local]
                continue


        if local is None:
            if not rule:
                raise InvalidConfig('Must use a "target_rule". %r' % branch)
            local = rule

        vrs.update({'version': key})
        try:
            local = _expand(local, vrs)
        except KeyError as e:
            raise InvalidConfig(miss_var % (e.message, key, branch))
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

