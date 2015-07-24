"""
    nx_tools.utils
    ~~~~~~~~~~~~~~

    Utility functions.
"""
import collections
import json
import logging
import os
import posixpath
import subprocess
from pprint import pformat

from .constants import DEFAULT_CONFIG_PATH, USER_CONFIG_PATH
from .exceptions import UserConfigNotFound


def is_cygwin_path(path):
    """Determines if path is Cygwin.

    msysGit paths do not count as being Cygwin, since they're regular POSIX.
    """
    if path[:9] == '/cygdrive':
        return True
    else:
        return False


def is_running_cygwin():
    try:
        pwd = os.environ['PWD']
    except KeyError:
        return False
    else:
        if is_cygwin_path(pwd):
            return True
        else:
            return False


def cygwpath(path):
    CYGPATH = r'C:\GnuNT\bin\cygpath.exe'
    cmd = [CYGPATH] + ['-w', path]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return proc.stdout.read().rstrip()  # Remove trailing newline


def xabspath(path):
    """Return the absolute path of given `path`.

    Works for Cygwin, msysGit and Windows style paths.

    Args:
        path (str) : Pathname to absolutize.
    """

    if posixpath.isabs(path):  # Starts with "/"
        if not is_cygwin_path(path):
            path = posixpath.join('/cygdrive', path[1:])
        return cygwpath(path)
    return os.path.abspath(path)


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
    """Read default configuration from DEFAULT_CONFIG_PATH.

    Returns:
        dict

    Raises:
        AssertionError: If the config cannot be found.
            This is supposed to be in package_data"""
    try:
        return load_json(DEFAULT_CONFIG_PATH)
    except IOError:
        raise AssertionError("Could not find default config at %s "
                             % DEFAULT_CONFIG_PATH)


def read_user_config():
    """Read user configuration from USER_CONFIG_PATH.

    Returns:
        dict

    Raises:
        UserConfigNotFound
    """
    try:
        return load_json(USER_CONFIG_PATH)
    except IOError:
        raise UserConfigNotFound("Could not find user config at %s "
                                 % USER_CONFIG_PATH)
    except ValueError:
        raise UserConfigNotFound("Not a JSON object")


def read_config():
    """Read a combined user/default config.

    User takes precedence over default.

    Returns:
        dict
    """
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
    """Simply determines if `value` is an executable file.

    Returns:
        bool"""
    if value[-4:] == '.exe':
        return True
    else:
        return False


def pformat_cli_args(locs):
    """Pretty format locals.

    To be used in to logger.debug input arguments of a CLI command. The 'conf'
    key is always ignored.

    Args:
        locs (dict): Local symbol table

    Returns:
        str
    """
    return 'ARGS\n' + '\n'.join(('%s : %s' % (k, v) for k, v in locs.iteritems()
                                if k[:4] != 'conf' and k[:3] != 'log'))


def _get_roots(config, nx_version, key):
    """Get root directories.

    Args:
        config (dict) : configuration
        nx_version (str) : NX version
        key (str) : 'remote' or 'local'

    Returns:
        tuple : (Root build directory, Root patches directory)
    """
    build = config[key]['build'][nx_version]
    try:
        patch = config[key]['patch'][nx_version]
    except KeyError:
            patch = config[key]['patch'][nx_version[:4]]

    return build, patch


def get_remote_roots(config, nx_version):
    return _get_roots(config, nx_version, 'remote')


def get_local_roots(config, nx_version):
    return _get_roots(config, nx_version, 'local')
