import io
import ftplib
import os
import shutil
import time
import threading
import zipfile

import pytest
import pyftpdlib.handlers
import pyftpdlib.authorizers
import pyftpdlib.servers

from nx_tools.api import update as nxup
from nx_tools.api.exceptions import NXToolsError
import nx_tools

from .conftest import maya


_7Z_ATTR = '_7Z_EXE'


class DummyTask(nxup._Task):

    def __init__(self, *args):
        super(DummyTask, self).__init__(*args)
        self._sleep_time = 0.01

    def run(self):
        time.sleep(self._sleep_time)
        return self.result

    def _set(self, result, sleep_time):
        self.result = result
        self._sleep_time = sleep_time


class DummyUpdater(nxup._Updater):

    task_cls = DummyTask
    def __init__(self, local_dir=None, remote_dir=None, delete_zip=None):
        super(DummyUpdater, self).__init__(local_dir, remote_dir, delete_zip)
        self._dummy_items = []

    def set_dummy_items(self, items):
        self._dummy_items = items

    def _list_items(self):
        return self._dummy_items


@pytest.fixture(scope='function')
def dumdir(tmpdir):
    return str(tmpdir.mkdir('temp'))


@pytest.fixture(scope='module')
def dummy_zip(tmpdir_factory):
    tmp = tmpdir_factory.mktemp('remote').mkdir('test_zip')
    tmp = str(tmp)
    td = os.path.join(tmp, 'testdir')
    os.mkdir(td)
    open(os.path.join(td, 'hello.txt'), 'w').write('content')
    zip_path = os.path.join(tmp, 'tmg11_win64_1234.zip')
    with open(zip_path, 'w') as fzip:
        z = zipfile.ZipFile(fzip, 'w')
        for root, dirs, files in os.walk(td):
            for f in files:
                fname = os.path.join(root, f)
                arcname = os.path.relpath(fname, tmp)
                z.write(fname, arcname)
        z.close()
    shutil.rmtree(td)
    return zip_path


@pytest.fixture(scope='function')
def local_zip(dummy_zip, dumdir):
    dest = os.path.join(dumdir, os.path.basename(dummy_zip))
    shutil.copy(dummy_zip, dest)
    return dest

@pytest.fixture(scope='function')
def dev_7z(monkeypatch):
    envar = 'NX_TOOLS_TEST_7Z_EXE'
    exe = os.environ.get(envar, None)
    if exe is None:
        exe = getattr(nxup, _7Z_ATTR)
    else:
        monkeypatch.setattr(nxup, _7Z_ATTR, exe)

    if not os.path.exists(exe):
        msg = '7Z executable at %s does not exist.\n' % exe
        msg += 'Specify using %s' % envar
        raise AssertionError(msg)


class FTPStubThread(threading.Thread):
    daemon = True
    _lock = threading.Lock()
    def __init__(self, host, port, user_root):
        self.host = host
        self.port = port
        self.user_root = user_root
        self._serving = False
        super(FTPStubThread, self).__init__()

    def run(self):
        authorizer = pyftpdlib.authorizers.DummyAuthorizer()
        authorizer.add_anonymous(self.user_root)
        handler = pyftpdlib.handlers.FTPHandler
        handler.authorizer = authorizer
        address = (self.host, self.port)
        self.server = pyftpdlib.servers.ThreadedFTPServer(address, handler)
        self._serving = True
        started = time.time()
        while self._serving:
            with self._lock:
                self.server.serve_forever(timeout=1, blocking=False)

            if (time.time() >= started + 10):
                self.server.close_all()
                raise Exception('ftp shutdown due to timeout')

        self.server.close_all()

    def stop(self):
        self._serving = False


@pytest.fixture(scope='module')
def ftpstub_module(dummy_zip, tmpdir_factory):
    port = 2122
    host = 'localhost'
    d = tmpdir_factory.mktemp('ftp').mkdir('remote')
    user_root = str(d)
    remote = str(d.mkdir('test_zip'))
    shutil.copy(dummy_zip, remote)
    assert os.path.exists(user_root)
    thread = FTPStubThread(host=host, port=port, user_root=user_root)
    thread.start()
    yield (host, port)
    thread.stop()


@pytest.fixture(scope='function')
def ftpstub(ftpstub_module, monkeypatch):
    host, port = ftpstub_module
    monkeypatch.setattr(nxup, '_FTP_HOSTNAME', host)
    monkeypatch.setattr(nxup, '_FTP_PORT', port)


def assert_zip_contents(root):
    d = os.path.join(root, 'tmg11_win64_1234')
    assert os.path.exists(d)
    assert os.path.isdir(d)
    sub = os.path.join(d, 'testdir')
    assert os.path.exists(sub)
    assert os.path.isdir(sub)
    f = os.path.join(sub, 'hello.txt')
    assert os.path.exists(f)
    assert os.path.isfile(f)
    assert open(f).read() == 'content'


def assert_task_success(task, local, fname, dz):
    results = []
    for r in nxup.submit_tasks([task,]):
        results.append(r)

    assert len(results) == 1
    result = results[0]
    assert result.stat == nxup.TASK_SUCCESS
    assert result.item == fname
    local_zip = os.path.join(local, fname)
    exp = os.path.exists(local_zip)
    if dz:
        exp = not exp
    assert exp
    assert_zip_contents(local)
    assert result.item == fname


def assert_update_success(up, local, fname, dz):
    new = up.list_new()
    assert len(new) == 1 and new[0] == fname
    tasks = up.make_tasks([0,])
    assert len(tasks) == 1
    assert_task_success(tasks[0], local, fname, dz)


dz_true_false = pytest.mark.parametrize("dz", [(True), (False)])


def test_submit_tasks():
    times = [0.5, 0.2]
    results = [
        nxup.TaskResult(item=0, stat=nxup.TASK_SUCCESS, reason=None),
        nxup.TaskResult(item=1, stat=nxup.TASK_FAIL, reason='foo')
    ]
    tasks = []
    for t, result in zip(times, results):
        task = DummyTask(None, None, None, None, None)
        task._set(result, t)
        tasks.append(task)

    i = -1
    t0 = time.time()
    for r in nxup.submit_tasks(tasks):
        i += 1
        t1 = time.time()
        if i == 0:
            expect = 1
            ttol = 0.3
        elif i == 1:
            expect = 0
            ttol = 0.6
        else:
            raise AssertionError('Too many results')
        assert r == results[expect]
        assert t1 - t0 <= ttol


@dz_true_false
def test_tmg_update(ftpstub, dev_7z, dumdir, dummy_zip, dz):
    remote = os.path.basename(os.path.dirname(dummy_zip))
    fname = os.path.basename(dummy_zip)
    local = dumdir
    up = nxup.TMGUpdater(local, remote, dz)
    assert_update_success(up, local, fname, dz)


@dz_true_false
def test_nx_update(dev_7z, dumdir, dummy_zip, dz):
    remote, fname = os.path.split(dummy_zip)
    local = dumdir
    up = nxup.NXUpdater(local, remote, dz)
    assert_update_success(up, local, fname, dz)


@dz_true_false
def test_tmg_task_success(ftpstub, dev_7z, dumdir, dummy_zip, dz):
    remote = os.path.basename(os.path.dirname(dummy_zip))
    fname = os.path.basename(dummy_zip)
    local = dumdir
    task = nxup.TMGTask(0, local, remote, fname, dz)
    assert_task_success(task, local, fname, dz)


@dz_true_false
def test_nx_task_success(dev_7z, dumdir, dummy_zip, dz):
    remote, fname = os.path.split(dummy_zip)
    local = dumdir
    task = nxup.NXTask(0, local, remote, fname, dz)
    assert_task_success(task, local, fname, dz)


def test_nx_task_fail(dumdir, dummy_zip):
    remote, fname = os.path.split(dummy_zip)
    task = nxup.NXTask(0, dumdir, 'doesnotexist', fname, False)
    assert task.run().stat == nxup.TASK_FAIL
    task = nxup.NXTask(0, dumdir, remote, 'nope', False)
    assert task.run().stat == nxup.TASK_FAIL


def test_make_tasks(dumdir):
    kwargs = dict(local_dir=dumdir, remote_dir='remote', delete_zip=True)
    up = DummyUpdater(**kwargs)
    new_items = [5, 6, 7]
    up._new_items = new_items
    tasks = up.make_tasks(range(len(new_items)))

    def assert_all(func):
        assert all([func(i, t) for i, t in enumerate(tasks)])

    def test_type(i, t):
        return type(t) == DummyTask

    def test_kwarg(kw, datum):
        def func(i, t):
            return getattr(t, '_' + kw) == datum
        return func

    def test_item(i, t):
        return t.item == new_items[i]

    assert_all(test_type)
    for kw, datum in kwargs.items():
        assert_all(test_kwarg(kw, datum))
    assert_all(test_item)


def test_make_tasks_local_dir_does_not_exist(tmpdir):
    local_dir = os.path.join(str(tmpdir), 'local_dir')
    up = DummyUpdater(local_dir=local_dir)
    up._new_items = ['a', 'b']
    up.make_tasks([0, 1])
    assert os.path.exists(local_dir)


def test_make_tasks_no_ids(dumdir):
    up = DummyUpdater(dumdir)
    up._new_items = ['a', 'b']
    assert up.make_tasks([]) == []


def test_make_tasks_invalid_ids(dumdir):
    up = DummyUpdater(dumdir)
    up._new_items = ['a', 'b', 'c']
    ids = [-1, 0]
    with pytest.raises(NXToolsError):
        up.make_tasks(ids)

    ids = [0, 4]
    with pytest.raises(NXToolsError):
        up.make_tasks(ids)


def test_make_tasks_before_list(dumdir):
    up = DummyUpdater(local_dir=dumdir)
    assert up.make_tasks([0, 1]) == []


def test_make_task_ids(dumdir):
    ids = [5, 10, 2]
    up = nxup.TMGUpdater
    expected = ['TMGUpdater-%i' % i for i, _ in enumerate(ids)]
    assert up._mk_task_ids(ids) == expected
    up = nxup.NXUpdater
    expected = ['NXUpdater-%i' % i for i, _ in enumerate(ids)]
    assert up._mk_task_ids(ids) == expected


def test_list_new(tmpdir):
    d = tmpdir.mkdir('list_new')
    up = DummyUpdater(local_dir=str(d))
    assert up.list_new() == []
    items = ['first', 'second', 'third']
    up.set_dummy_items(items)
    d.mkdir('first')
    assert up.list_new() == ['second', 'third']
    d.mkdir('third')
    assert up.list_new() == ['second']


def test_is_new(tmpdir):
    name = 'nx11_0123'
    d = tmpdir.mkdir('is_new')
    d.join(name + '.zip')
    up = DummyUpdater(local_dir=str(d))
    assert up._is_new(name)
    d.mkdir(name)
    assert not up._is_new(name)


def test_ftp_invalid_dir(ftpstub):
    with pytest.raises(NXToolsError):
        with nxup._ftp_client('doesnotexist') as f:
            pass


def test_windows_item():
    dat = [
        ('nx11_wntx64_01234.zip', True),
        ('nx09_1234_win64.zip', True),
        ('nx11_linux_1264.zip', False)
    ]
    fnames, expected = zip(*dat)
    func = nxup.TMGUpdater._is_windows_item
    res = [func(f) for f in fnames]
    assert list(expected) == res


def test_extract(dev_7z, local_zip):
    nxup._extract(local_zip)
    assert_zip_contents(os.path.dirname(local_zip))


@maya('Extract')
def test_default_extract(local_zip):
    nxup._extract(local_zip)
    assert_zip_contents(os.path.dirname(local_zip))


def test_extract_executable_does_not_exist(dumdir, monkeypatch, local_zip):
    exe = os.path.join(dumdir, 'nonexistent', '7z.exe')
    monkeypatch.setattr(nxup, _7Z_ATTR, exe)
    assert not os.path.exists(exe)
    try:
        nxup._extract(local_zip)
    except NXToolsError as e:
        assert exe in e.message


def test_extract_nonexistent_archive(dev_7z):
    fname = 'doesnotexist.7z'
    try:
        nxup._extract(fname)
    except NXToolsError as e:
        assert fname in e.message

