from __future__ import print_function

import logging
import os
import subprocess

import click

from .. import utils
from ..constants import USER_ROOT


@click.command('add_task',
               short_help='Add Updater to Windows Task Scheduler.')
@click.pass_obj
def cli(config):
    logger = logging.getLogger(__name__)
    props = []
    taskrun = '\"task_update.exe %s\"' % os.path.join(USER_ROOT, 'tasklog.log')
    props.append('/TR %s' % taskrun)
    taskname = 'Update NX11'
    props.append('/TN \"%s\"' % taskname)
    schedule = 'HOURLY'
    props.append('/SC %s' % schedule)
    starttime = '00:00'
    props.append('/ST %s' % starttime)
    props.append('/F')
    cmd = "schtasks /Create " + ' '.join(props)
    logger.debug("Running command:\n%s" % cmd)
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    if proc.returncode == 0:
        utils.ensure_dir_exists(USER_ROOT)
