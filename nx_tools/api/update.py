'''
Functions for updating NX patch and build.
'''
import collections
import ftplib
import glob
import logging
from multiprocessing.dummy import Pool as ThreadPool
import os
import shutil
from subprocess import Popen, PIPE
import sys

from . import utils
from .exceptions import *

logger = logging.getLogger(__name__)

_MAX_WORKERS = 3

Task = collections.namedtuple('Task', ('func', 'args'))
TaskResult = collections.namedtuple('TaskResult', ('stat', 'reason'))
TASK_SUCCESS = 0
TASK_FAIL = 1
TASK_ASSERT = -1


def submit_tasks(tasks):
    pool = Pool(_MAX_WORKERS)
    return pool.imap_unordered(run_task, tasks)


class _Task(object):
    def __init__(self, local_dir, remote_dir, item, delete_zip):
        self._local_dir = local_dir
        self._remote_dir = remote_dir
        self._item = item
        self._delete_zip = delete_zip

    def run(self):
        stat = TASK_SUCCESS
        reason = None
        try:
            dest_zip = os.path.join(self._local_dir, self._item)
            logger.debug('Fetching %s to %s.' % (self._item, dest_zip))
            self._fetch(dest_zip)
            logger.debug('Fetch to %s complete.' % dest_zip)
            logger.debug('Extracting: '  + dest_zip)
            _extract(dest_zip)
            if self._delete_zip:
                logger.debug('Deleting archive: ' + dest_zip)
                os.remove(dest_zip)
        except Exception as e:
            stat = TASK_FAIL
            reason = e.message
            if not type(e) == NXToolsError:
                msg = 'Task encountered non-NXToolsError exception.\n%s' % self
                logger.error(msg)
                logger.error(e, exc_info=True)
                reason = 'UNEXPECTED ASSERT. CHECK LOG'

        return TaskResult(stat, reason)

    def __str__(self):
        s =  'Local: %s - ' % self._local_dir
        s += 'Remote: %s - ' % self._remote_dir
        s += 'Item: %s' % self._item
        return s

    def _fetch(self, dest_zip):
        raise NotImplementedError


class TMGTask(_Task):
    def _fetch(self, dest_zip):
        ftp = TMGUpdater._ftp_connect(self._local_dir)
        try:
            with open(dest_zip, 'wb') as fh:
                ftp.retrbinary('RETR ' + self._item, fh.write)
        except IOError as e:
            msg = 'Could not write to %s.\n%s' % (dest_zip, e.message)
            raise NXToolsError(msg)
        finally:
            ftp.close()


class NXTask(_Task):
    def _fetch(self, dest_zip):
        src = os.path.join(self._local_dir, self._item)
        try:
            shutil.copy(src, dest_zip)
        except IOError as e:
            raise NXToolsError('Could not copy %s to %s' % self._item, dest_zip)

class _Updater(object):

    items_key = None
    task_cls = None

    @classmethod
    def from_config(cls, config, nx_version):
        assert items_key is not None
        assert task_cls is not None
        local = config.get_local(items_key, nx_version)
        remote = config.get_remote(items_key, nx_version)
        dz = config.get('delete_zip')
        return cls(
            local_dir=local,
            remote_dir=remote,
            delete_zip=dz,
        )

    def __init__(self, local_dir, remote_dir, delete_zip):
        self._local_dir = local_dir
        self._remote_dir = remote_dir
        self._dz = delete_zip
        self._new_items = []

    def list_new(self):
        items = self._list_items()
        logger.debug('Found items:\n' + '\n'.join(items))
        self._new_items = [it for it in items if self._is_new(it)]
        return self._new_items

    def make_tasks(self, ids):
        if not self._new_items:
            return []

        utils.ensure_dir_exists(self._local_dir)
        num_items = len(self._new_items)
        invalid_ids = [i for i, n in enumerate(ids) if n < 0 or n >= num_items]
        if invalid_ids:
            raise NXToolsError('Invalid IDs for tasks: ' + ', '.join(invalid_ids))

        ld = self._local_dir
        rd = self._remote_dir
        dz = self._dz
        tasks = [
            self.task_cls(ld, rd, self._new_items[i], dz)
            for i in ids
        ]

    def _is_new(self, f):
        r = is_new(f, self._local_dir)
        logger.debug('Item %s is new? %r' % (f, r))
        return r

    def _list_items(self):
        raise NotImplementedError


class NXUpdater(_Updater):

    items_key = 'nx'
    task_cls = NXTask

    def _list_files(d):
        return [f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]

    def _list_items(self):
        if not os.path.exists(self._remote_dir):
            msg = 'NX remote directory does not exist: ' + self._remote_dir
            raise NXToolsError(msg)

        files = _list_files(self._remote_dir)
        logger.debug(
            'NX Remote %s contains:\n%s'
            % (self._remote_dir, '\n'.join(files))
        )
        matches = [f for f in files if os.path.splitext(f)[1] == '.7z']
        return matches


class TMGUpdater(_Updater):

    items_key = 'tmg'
    task_cls = TMGTask

    def _list_items(self):
        ftp = self._connect(self._local_dir)
        fnames = ftp.nlst()
        ftp.close()
        logger.debug('FTP Listing: %s\n' + '\n'.join(names))

        return [f for f in fnames if self._is_windows_item(f)]

    @staticmethod
    def _is_windows_item(fname):
        return 'wntx64' in fname or 'win64' in fname

    @staticmethod
    def _ftp_connect(pathname):
        logger.debug('Creating FTP connection in directory: ' + pathname)
        try:
            ftp = ftplib.FTP('ftp')
            ftp.login()
            ftp.cwd(pathname)
        except ftplib.all_errors as e:
            ftp.close()
            raise NXToolsError('FTP connection error:\n' + e.message)

        return ftp


def is_new(f, target_dir):
    filename = utils.get_filename(f)
    if os.path.isdir(os.path.join(target_dir, filename)):
        return False
    return True


def _extract(zip_path):
    exe_7z = 'C:\\Program Files\\7-Zip\\7zG.exe'
    if not os.path.exists(zip_path):
        raise NXToolsError('Archive does not exist: %s' % zip_path)
    output_dir = os.path.splitext(zip_path)
    command = [exe_7z, 'x', zip_path, '-o' + output_dir]
    logger.debug('Extract command: ' + ' '.join(command))
    try:
        p = Popen(command, stdout=PIPE, stderr=PIPE)
    except WindowsError:
        raise NXToolsError('Could not find 7-Zip at %s.' % exe_7z)
    p.wait()
    if p.returncode != 0:
        out, _ = process.communicate()
        errmsg = out.decode('utf-8')
        raise NXToolsError('Could not extract successfully.\n' + errmsg)
    logger.debug('File successfully extracted to: ' + output_dir)

