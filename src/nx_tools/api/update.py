from contextlib import contextmanager
import collections
import ftplib
import logging
import os
import shutil
from multiprocessing.dummy import Pool as ThreadPool
from subprocess import PIPE, Popen

from . import utils
from .exceptions import NXToolsError

logger = logging.getLogger(__name__)

_MAX_WORKERS = 3
_FTP_HOSTNAME = 'ftp'
_FTP_PORT = 0  # Default FTP port
_7Z_EXE = 'C:\\Program Files\\7-Zip\\7zG.exe'

TaskResult = collections.namedtuple('TaskResult', ('id', 'stat', 'reason'))
TASK_SUCCESS = 0
TASK_FAIL = 1
TASK_ASSERT = 2


def submit_tasks(tasks):
    def run_task(task):
        return task.run()
    pool = ThreadPool(_MAX_WORKERS)
    return pool.imap_unordered(run_task, tasks)


class _Task(object):
    def __init__(self, id_, local_dir, remote_dir, item, delete_zip):
        self._local_dir = local_dir
        self._remote_dir = remote_dir
        self._item = item
        self._delete_zip = delete_zip
        self._id = id_

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
        except NXToolsError as e:
            stat = TASK_FAIL
            reason = e.message
        except Exception as e:
            stat = TASK_ASSERT
            msg = 'Task encountered non-NXToolsError exception.\n%s' % self
            logger.error(msg)
            logger.error(e, exc_info=True)
            reason = 'UNEXPECTED ASSERT. CHECK LOG'

        return TaskResult(self._id, stat, reason)

    def __str__(self):
        s = self._id + '< '
        s +=  'Local: %s - ' % self._local_dir
        s += 'Remote: %s - ' % self._remote_dir
        s += 'Item: %s' % self._item
        s += ' >'
        return s

    def _fetch(self, dest_zip):
        raise NotImplementedError


class TMGTask(_Task):
    def _fetch(self, dest_zip):
        with _ftp_client(self._remote_dir) as ftp:
            with open(dest_zip, 'wb') as fh:
                ftp.retrbinary('RETR ' + self._item, fh.write)
#       except IOError as e:
#           msg = 'Could not write to %s.\n%s' % (dest_zip, e.message)
#           raise NXToolsError(msg)


class NXTask(_Task):
    def _fetch(self, dest_zip):
        src = os.path.join(self._remote_dir, self._item)
        try:
            shutil.copy(src, dest_zip)
        except IOError as e:
            raise NXToolsError('Could not copy %s to %s' % (self._item, dest_zip))

class _Updater(object):

    task_cls = None

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
        invalid_ids = [str(i) for i, n in enumerate(ids) if n < 0 or n >= num_items]
        if invalid_ids:
            raise NXToolsError('Invalid IDs for tasks: ' + ', '.join(invalid_ids))

        ld = self._local_dir
        rd = self._remote_dir
        dz = self._dz
        task_ids = self._mk_task_ids(ids)
        tasks = [
            self.task_cls(task_ids[i], ld, rd, self._new_items[it], dz)
            for i, it in enumerate(ids)
        ]
        return tasks

    @classmethod
    def _mk_task_ids(cls, ids):
        return ['%s-%i' % (cls.__name__, i) for i, _ in enumerate(ids)]

    def _is_new(self, f):
        r = is_new(f, self._local_dir)
        logger.debug('Item %s is new? %r' % (f, r))
        return r

    def _list_items(self):
        raise NotImplementedError


class NXUpdater(_Updater):

    task_cls = NXTask

    def _list_items(self):
        if not os.path.exists(self._remote_dir):
            msg = 'NX remote directory does not exist: ' + self._remote_dir
            raise NXToolsError(msg)

        files = [f for f in os.listdir(self._remote_dir)
                 if os.path.isfile(os.path.join(self._remote_dir, f))]
        logger.debug(
            'NX Remote %s contains:\n%s'
            % (self._remote_dir, '\n'.join(files))
        )
        matches = [f for f in files if os.path.splitext(f)[1] == '.7z']
        return matches


class TMGUpdater(_Updater):

    task_cls = TMGTask

    def _list_items(self):
        with _ftp_client(self._remote_dir) as ftp:
            fnames = ftp.nlst()
        logger.debug('FTP Listing: %s\n' + '\n'.join(fnames))

        return [f for f in fnames if self._is_windows_item(f)]

    @staticmethod
    def _is_windows_item(fname):
        return 'wntx64' in fname or 'win64' in fname


def is_new(f, target_dir):
    filename = utils.get_filename(f)
    if os.path.isdir(os.path.join(target_dir, filename)):
        return False
    return True


@contextmanager
def _ftp_client(pathname):
    logger.debug('Creating FTP connection in directory: ' + pathname)
    try:
        ftp = ftplib.FTP()
        ftp.connect(_FTP_HOSTNAME, _FTP_PORT)
        ftp.login()
        ftp.cwd(pathname)
        yield ftp
    except ftplib.all_errors as e:
        ftp.close()
        raise NXToolsError('FTP connection error:\n%s' % e)
    finally:
        ftp.close()


def _extract(zip_path):
    if not os.path.exists(zip_path):
        raise NXToolsError('Archive does not exist: %s' % zip_path)
    output_dir, _ = os.path.splitext(zip_path)
    command = [_7Z_EXE, 'x', zip_path, '-o' + output_dir]
    logger.debug('Extract command: ' + ' '.join(command))
    try:
        p = Popen(command, stdout=PIPE, stderr=PIPE)
    except OSError:
        raise NXToolsError('Could not find 7-Zip at %s.' % _7Z_EXE)
    p.wait()
    if p.returncode != 0:
        out, _ = process.communicate()
        errmsg = out.decode('utf-8')
        raise NXToolsError('Could not extract successfully.\n' + errmsg)
    logger.debug('File successfully extracted to: ' + output_dir)

