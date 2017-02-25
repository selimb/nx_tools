from __future__ import print_function

import logging
import os
import subprocess

import click

from ..constants import PKG_BIN


@click.command('identifier', short_help='Launch identifier.')
@click.pass_obj
def cli(config):
    identifier = os.path.join(PKG_BIN, 'nx_identifier.exe')
    logger = logging.getLogger(__name__)
    cmd = [identifier, config['identifier_hotkey']]
    logger.debug("Calling %s" % cmd)
    subprocess.Popen(cmd)
