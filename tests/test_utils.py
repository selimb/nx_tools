import os
import pytest

from nx_tools.api import utils
from nx_tools.constants import DEFAULT_CONFIG_PATH


def test_load_json(tmpdir):
    tmp = str(tmpdir)
    fpath = os.path.join(tmp, 'config.json')
    open(fpath, 'w').write('{"tmg": {"nx9": "Hello\\World"}}')


def test_load_json_invalid(tmpdir):
    tmp = str(tmpdir)
    fpath = os.path.join(tmp, 'config.json')
    open(fpath, 'w').write('{"tmg": {"first": 1 "second": 2}}')
    with pytest.raises(ValueError):
        utils.load_json(fpath)


def test_can_load_default_config():
    utils.load_json(DEFAULT_CONFIG_PATH)


def test_load_json_nonexistent():
    with pytest.raises(IOError):
        utils.load_json('nonexistent')


def test_load_json_windows_paths(tmpdir):
    tmp = str(tmpdir)
    fpath = os.path.join(tmp, 'config.json')
    open(fpath, 'w').write(r'{"tmg": {"nx9": "C:\Users\foo"}}')
    d = utils.load_json(fpath)
    assert d['tmg']['nx9'] == r'C:\Users\foo'


def test_write_json(tmpdir):
    tmp = str(tmpdir)
    d = os.path.join(tmp, 'dirdoesnotexistyet')
    fpath = os.path.join(d, 'config.json')
    d = {}
    d['tmg'] = {'nx9': 'asdf'}
    utils.write_json(d, fpath)
    assert os.path.exists(fpath)


def test_ensure_dir_exists(tmpdir):
    root = str(tmpdir)
    d = os.path.join(root, 'testdir', 'nested')
    utils.ensure_dir_exists(d)
    assert os.path.exists(d) and os.path.isdir(d)
    f = os.path.join(d, 'file')
    open(f, 'w').write('h')
    utils.ensure_dir_exists(d)
    assert open(f).read() == 'h'


def test_get_filename(tmpdir):
    fp = tmpdir.mkdir('tmp').join('hello_._world.7z')
    assert utils.get_filename(str(fp)) == 'hello_._world'

