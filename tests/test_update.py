import os
import pytest
import zipfile

from nx_tools.api import update as nxup
from nx_tools.exceptions import NXToolsError

from .conftest import production

class DummyUpdater(nxup._Updater):
    def __init__(self, local_dir=None, remote_dir=None, delete_zip=None):
        super(DummyUpdater, self).__init__(local_dir, remote_dir, delete_zip)
        self._dummy_items = []

    def set_dummy_items(self, items):
        self._dummy_items = items

    def _list_items(self):
        return self._dummy_items

    def _make_task(self, i):
        return i

    @staticmethod
    def task_func():
        pass

@pytest.fixture(scope='function')
def temp_zip(tmpdir):
    f = tmpdir.mkdir('test_zip').join('test123.zip')
    z = zipfile.ZipFile(f, 'w')
    z.write(os.path.join('testdir', 'test.txt'))
    z.close()
    return z

def test_extract(temp_zip):
    raise NotImplementedError

def test_windows_item():
    dat = [
        ('nx11_wntx64_01234.zip', True)
        ('nx09_1234_win64.zip', True)
        ('nx11_linux_1264.zip', False)
    ]
    fnames, expected = zip(*dat)
    func = nxup.TMGUpdater._is_windows_item
    res = [func(f) for f in fnames]
    assert expected == res

def test_parse_listings():
    raise NotImplementedError

@production
def test_ftp_connect_defaults():
    raise NotImplementedError
    dirs = []
    for d in dirs:
        ftp = nxup.TMGUpdater._ftp_connect(d)
        ftp.close()

@production
def test_ftp_invalid_dir():
    raise NotImplementedError

def test_make_tasks_before_list():
    up = DummyUpdater()
    assert up.make_tasks([0, 1]) == []

def test_make_tasks_invalid_ids():
    up = DummyUpdater()
    up.new_items = ['a', 'b', 'c']
    ids = [-1, 0]
    with pytest.raises(NXToolsError):
        up.make_tasks(ids)

    ids = [0, 4]
    with pytest.raises(NXToolsError):
        up.make_tasks(ids)

def test_is_new(tmpdir):
    name 'nx11_0123'
    d = tmpdir.mkdir('is_new')
    d.join(name + '.zip')
    up = DummyUpdater(local_dir=d)
    assert up._is_new(name)
    d.mkdir(name)
    assert not up._is_new(name)

def test_list_new(tmpdir):
    d = tmpdir.mkdir('list_new')
    up = DummyUpdater(local_dir=d)
    assert up.list_new() == []
    items = ['first', 'second', 'third']
    up.set_dummy_items(items)
    d.mkdir('first')
    assert up.list_new() == ['second', 'third']
    d.mkdir('third')
    assert up.list_new() == ['second']
