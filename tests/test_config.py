import os
import pytest

import nx_tools.api.config as nxconfig
from nx_tools.api.exceptions import UserConfigInvalid, UserConfigNotFound


def test_split_merged_does_not_mutate_input():
    d0 = {'nx10,nx1002': 'a'}
    d = d0.copy()
    nxconfig._split_merged(d)
    assert d == d0


def test_split_merged_no_modifications_needed():
    d = {'nx10': 'a', 'nx9': 'b'}
    r = nxconfig._split_merged(d)
    assert r == d


def test_split_merged_full():
    keys = ['nx10', 'nx1001', 'nx1002']
    d = {}
    d[','.join(keys)] = 'a'
    d['nx9'] = 'b'
    expected = {'nx9': 'b'}
    for k in keys:
        expected[k] = 'a'
    r = nxconfig._split_merged(d)
    assert expected == r


def test_split_merged_error_on_duplicate_entries():
    d = {'nx9,nx10': 'a', 'nx10': 'b'}
    with pytest.raises(UserConfigInvalid):
        nxconfig._split_merged(d)


def test_fuzzy_version_no_match():
    nx_version = 'nx10'
    available = ['nx9', 'nx11']
    with pytest.raises(UserConfigInvalid):
        nxconfig._fuzzy_version(nx_version, available)


def test_fuzzy_version_ambiguous():
    nx_version = 'nx901'
    available = ['nx9', 'nx90', 'nx10']
    with pytest.raises(UserConfigInvalid):
        nxconfig._fuzzy_version(nx_version, available)


def test_fuzzy_version_exact_match():
    nx_version = 'nx10'
    available = ['nx10', 'nx9']
    assert nxconfig._fuzzy_version(nx_version, available) == nx_version
    available.append('nx1001')
    assert nxconfig._fuzzy_version(nx_version, available) == nx_version


def test_fuzzy_version_fuzzy_match():
    nx_version = 'nx1001'
    available = ['nx9', 'nx10', 'nx11']
    assert nxconfig._fuzzy_version(nx_version, available) == 'nx10'


def test_recursive_dict_update():
    d = {
        'tmg': {
            'nx9': 'a'
        },
        'default': 'blah',
        'override': None
    }
    u = {'tmg': {'nx9': 'b'}, 'override': 'user'}
    r = nxconfig._recursive_dict_update(d, u)
    assert r['default'] == 'blah'
    assert r['override'] == 'user'
    assert r['tmg']['nx9'] == 'b'


def test_load_json_nonexistent():
    with pytest.raises(IOError):
        nxconfig._load_json('nonexistent')


def test_load_json_windows_paths(tmpdir):
    tmp = str(tmpdir)
    fpath = os.path.join(tmp, 'config.json')
    open(fpath, 'w').write(r'{"tmg": {"nx9": "C:\Users\foo"}}')
    d = nxconfig._load_json(fpath)
    assert d['tmg']['nx9'] == r'C:\Users\foo'


def test_write_json(tmpdir):
    tmp = str(tmpdir)
    d = os.path.join(tmp, 'dirdoesnotexistyet')
    fpath = os.path.join(d, 'config.json')
    d = {}
    d['tmg'] = {'nx9': 'asdf'}
    nxconfig._write_json(d, fpath)
    assert os.path.exists(fpath)


def test_can_read_default_config():
    nxconfig._read_default_config()


def test_read_user_config_error_not_found():
    with pytest.raises(UserConfigNotFound):
        nxconfig._read_user_config('doesnotexist')


def test_read_user_config_invalid(tmpdir):
    tmp = str(tmpdir)
    fpath = os.path.join(tmp, 'config.json')
    open(fpath, 'w').write('{"tmg": {"first": 1 "second": 2}}')
    with pytest.raises(UserConfigInvalid):
        nxconfig._read_user_config(fpath)


def test_expand_config():
    d = {

    }


def test_config_dummy_simple(tmpdir):
    def mk(d):
        return [str(d.mkdir('remote')), str(d.mkdir('local'))]
    d = {'stuff': 'foo', 'tmg': {}, 'nx': {}}
    nx_versions = ['nx9', 'nx10']
    for v in nx_versions:
        root = tmpdir.mkdir(v)
        patches = root.mkdir('patches')
        builds = root.mkdir('builds')
        d['tmg'][v] = mk(patches)
        d['nx'][v] = mk(builds)
    conf = nxconfig.Config(d)
    assert conf.get('stuff') == 'foo'
    with pytest.raises(AssertionError):
        conf.get('nope')
    # assert sort(conf.list_versions()) == nx_versions
