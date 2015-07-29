"""

This command is required by nx_launch
"""

import click
import logging
import os
import time

from .. import utils

FMT = "{0}. {1} -- created: {2}"


def list_directories(root_dir):
    """List absolute paths to directories inside `root_dir`.

    Directories are listed in reverse alphabetical order.

    Returns:
        list
    """
    logger = logging.getLogger(__name__)
    logger.debug('Listing directories in %s' % root_dir)
    directories = []
    for d in os.listdir(root_dir):
        path = os.path.join(root_dir, d)
        if os.path.isdir(path):
            directories.append(path)
    return directories[::-1]


def fmt_ctime(x):
    t = time.gmtime(os.path.getctime(x))
    return time.strftime("%a %b %d", t)


def pformat_directories(l, absolute=False):
    """Pretty print directory listing.

    Directories are listed along with the file creation date.
    """
    def fmt_dir(index, directory, absolute):
        transform = os.path.basename
        if absolute:
            transform = lambda x: x
        return FMT.format(index, transform(directory), fmt_ctime(directory))

    return '\n'.join(fmt_dir(i, d, absolute=absolute)
                     for i, d in enumerate(l))


@click.command('list', short_help='List available builds and patches.')
@click.argument('nx_version', nargs=1)
@click.option('-b', '--build', is_flag=True,
              help='Only list builds.')
@click.option('-p', '--patch', is_flag=True,
              help='Only list patches.')
@click.option('--absolute', is_flag=True,
              help='List absolute paths')
@click.pass_obj
def cli(config, nx_version, build, patch, absolute):
    logger = logging.getLogger(__name__)
    logger.debug(utils.pformat_cli_args(locals()))

    def do_print(header, root):
        print(header)
        print(pformat_directories(list_directories(root),
                                  absolute=absolute))

    build_root, patch_root = utils.get_local_roots(config, nx_version)
    logger.debug('Build root: %s' % build_root)
    logger.debug('Patch root: %s' % patch_root)
    header_build, header_patch = ["List of %s:" % x
                                  for x in ('builds', 'patches')]
    if build and patch:
        return
    if patch is False:
        if utils.is_exe(build_root):
            print("Frozen build.")
        else:
            do_print(header_build, build_root)
    if build is False:
        do_print(header_patch, patch_root)
