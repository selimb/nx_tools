"""
Functions for updating NX patch and build.
"""
import ftplib
import glob
import logging
import os
import shutil
import subprocess
import sys

from .. import utils
from ..exceptions import *

logger = logging.getLogger(__name__)


def get_process_output(process):
    errmsg, _ = process.communicate()
    errmsg = errmsg.decode("utf-8")
    return errmsg


def extract(archive_filepath, exe):
    """Extracts archive file to folder in same directory."""
    output_dir = os.path.join(os.path.dirname(archive_filepath),
                              get_filename(archive_filepath))
    command = [exe, "x", archive_filepath, "-o" + output_dir]
    logger.debug("Extracting: " + ' '.join(command))
    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except WindowsError:
        logger.error("Could not run " + exe)
        raise NXToolsError
    p.wait()
    if p.returncode != 0:
        process_output = get_process_output(process=p)
        logger.error("Could not extract successfully." + process_output)
        raise NXToolsError
    logger.debug("File successfully extracted to: " + output_dir)


def get_filename(filepath):
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    return filename


def delete_file(filepath):
    logger.debug("Deleting file: " + filepath)
    os.remove(filepath)


def is_new(f, target_dir):
    filename = get_filename(f)
    if os.path.isdir(os.path.join(target_dir, filename)):
        return False
    return True


class _Updater(object):

    item_name = None
    item_name_plural = None

    def __init__(self, nx_version, config, source_key):
        self.nx_version = nx_version.lower()
        try:
            self.remote_dir = config['remote'][source_key][nx_version]
            self.local_dir = config['local'][source_key][nx_version]
        except KeyError:
            raise ConfigError("Incomplete configuration for %s %s."
                    % (nx_version, self.item_name_plural))
        # TODO don't need these to be class attributes
        self.do_delete_zip = config["delete_zip"]
        self.zip_exe = config['7z_exe']
        utils.ensure_dir_exists(self.local_dir)

    def _is_new(self, f):
        return is_new(f, self.local_dir)

    def check_new(self):
        raise NotImplementedError

    def _transfer(self):
        raise NotImplementedError

    def fetch(self, item):
        dest_zip = os.path.join(self.local_dir, os.path.basename(item))
        try:
            self._transfer(item, dest_zip)
            extract(dest_zip, exe=self.zip_exe)
            if self.delete_zip == True:
                delete_file(dest_zip)
        except NXToolsError:
            logger.error(NXToolsError)


class _TMGUpdater(_Updater):
    item_name = 'patch'
    item_name_plural = 'patches'

    def __init__(self, nx_version, config):
        super(_TMGUpdater, self).__init__(nx_version, config, 'patch')
        _connect()

    def _connect(self):
        ftp = ftplib.FTP('ftp')
        ftp.login()
        ftp.cwd(self.remote_dir)
        self.ftp = ftp

    def check_new(self):
        def is_windows(filename):
            return 'wntx64' in filename or 'win64' in filename
        logger.debug("Checking for %s patch on FTP server: "
                % (self.nx_version.upper(), self.remote_dir))
        listings = []
        self.ftp.retrlines("LIST", listings.append)
        found = []
        names = [l.split(None, 8)[-1].lstrip() for l in listings]
        logger.debug("FTP Listing: %s", '\n'.join(names))
        windows_patches = [n for n in names if is_windows(n)]
        return [p for p in windows_patches if self._is_new(p)]

    def _transfer(self, ftp_file, dest_file):
        try:
            with open(dest_file, "wb") as fh:
                self.ftp.retrbinary("RETR " + ftp_file, fh.write)
        except IOError as e:
            raise NXToolsError("Error occured during transfer.\n%s" % e)


class _BuildUpdater(_Updater):
    item_name = 'build'
    item_name_plural = 'builds'

    def __init__(self, nx_version, config):
        super(_BuildUpdater, self).__init__(nx_version, config, 'build')

    def check_new(self):
        logger.debug("Checking for %s build in Luc's T drive: %s"
                % (self.nx_version.upper(), self.remote_dir))
        if not os.path.exists(self.remote_dir):
            logger.error("Can't find remote directory: %s" % self.remote_dir)
            return []

        builds = list(glob.glob(os.path.join(self.remote_dir, "*.7z")))
        logger.debug("Builds: \n%s" % '\n'.join(builds))
        return [build for build in builds if self._is_new(build)]

    def _transfer(self, src, dest):
        logger.debug("Copying: %s\nto: %s" % (src, dest))
        try:
            shutil.copy(src, dest)
        except IOError as e:
            raise NXToolsError("Could not copy.\n%s" % e)


@click.command('check', short_help="Used internally by the Task Scheduler.")
@click.argument('nx_version', nargs=1)
@click.pass_obj
def check_cli(config, nx_version):
    """
    Return Codes:
        200 : Nothing new
        201 : New Build
        202 : New Patch
        203 : Both New Build and New Patch
    """
    new_build = False
    new_patch = False
    if not is_frozen_build(nx_version, config):
        new_build = check_build(nx_version, config)
    new_patch = check_TMG(nx_version, config)
    if new_build and new_patch:
        print("New Build and Patch Available.")
        sys.exit(203)
    if new_build:
        print("New Build Available.")
        sys.exit(201)
    if new_patch:
        print("New Patch Available.")
        sys.exit(202)
    print("Nothing New")
    sys.exit(200)


