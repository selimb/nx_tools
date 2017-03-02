import os
import shutil
import zipfile

import pytest

from nx_tools.api import update as nxup
from nx_tools.api.exceptions import NXToolsError
import nx_tools

from .conftest import production


class DummyTask(nxup._Task):
    def _fetch(self, dest_zip):
        src = os.path.join(self.local_dir, self.item)
        shutil.copy(src, dest_zip)


class DummyUpdater(nxup._Updater):

    items_key = 'dumdum'
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


@pytest.fixture(scope='function')
def temp_zip(tmpdir):
    tmp = tmpdir.mkdir('test_zip')
    tmp = str(tmp)
    td = os.path.join(tmp, 'testdir')
    os.mkdir(td)
    open(os.path.join(td, 'hello.txt'), 'w').write('content')
    zip_path = os.path.join(tmp, 'test123.zip')
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


@production
def test_extract(temp_zip):
    nxup._extract(temp_zip)
    root = os.path.dirname(temp_zip)
    d = os.path.join(root, 'test123')
    assert os.path.exists(d)
    assert os.path.isdir(d)
    sub = os.path.join(d, 'testdir')
    assert os.path.exists(sub)
    assert os.path.isdir(sub)
    f = os.path.join(sub, 'hello.txt')
    assert os.path.exists(f)
    assert os.path.isfile(f)
    assert open(f).read() == 'content'


@production
def test_extract_nonexistent_archive():
    with pytest.raises(NXToolsError):
        nxup._extract('doesnotexist.7z')


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


@production
def test_ftp_invalid_dir():
    with pytest.raises(NXToolsError):
        nxup.TMGUpdater._ftp_connect('doesnotexist')


def test_is_new(tmpdir):
    name = 'nx11_0123'
    d = tmpdir.mkdir('is_new')
    d.join(name + '.zip')
    up = DummyUpdater(local_dir=str(d))
    assert up._is_new(name)
    d.mkdir(name)
    assert not up._is_new(name)


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


def test_make_task_ids(dumdir):
    ids = [5, 10, 2]
    up = nxup.TMGUpdater
    expected = ['TMGUpdater-%i' % i for i, _ in enumerate(ids)]
    assert up._mk_task_ids(ids) == expected
    up = nxup.NXUpdater
    expected = ['NXUpdater-%i' % i for i, _ in enumerate(ids)]
    assert up._mk_task_ids(ids) == expected


def test_make_tasks_before_list(dumdir):
    up = DummyUpdater(local_dir=dumdir)
    assert up.make_tasks([0, 1]) == []


def test_make_tasks_invalid_ids(dumdir):
    up = DummyUpdater(dumdir)
    up._new_items = ['a', 'b', 'c']
    ids = [-1, 0]
    with pytest.raises(NXToolsError):
        up.make_tasks(ids)

    ids = [0, 4]
    with pytest.raises(NXToolsError):
        up.make_tasks(ids)


def test_make_tasks_no_ids(dumdir):
    up = DummyUpdater(dumdir)
    up._new_items = ['a', 'b']
    assert up.make_tasks([]) == []


def test_make_tasks_local_dir_does_not_exist(tmpdir):
    local_dir = os.path.join(str(tmpdir), 'local_dir')
    up = DummyUpdater(local_dir=local_dir)
    up._new_items = ['a', 'b']
    up.make_tasks([0, 1])
    assert os.path.exists(local_dir)


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
        return t._item == new_items[i]

    assert_all(test_type)
    for kw, datum in kwargs.items():
        assert_all(test_kwarg(kw, datum))
    assert_all(test_item)


def test_empty_task_runs(dumdir):
    raise NotImplementedError
