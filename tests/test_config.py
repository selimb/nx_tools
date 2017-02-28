import os
import pytest

import nx_tools.api.config as nxconfig
from nx_tools.api.exceptions import UserConfigInvalid, UserConfigNotFound


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


def test_pop_vars_no_vars():
    d0 = {'foo': 'bar'}
    d = d0.copy()
    r = nxconfig._pop_vars(d)
    assert d == d0
    assert r == {}


def test_pop_vars():
    expected = {'HOME': 'homeval', 'HI': 'hello'}
    d0 = {'foo': 'bar', 'tmg': {'nx9': 'baz'}}
    d = d0.copy()
    d.update(expected)
    user_vars = nxconfig._pop_vars(d)
    assert user_vars == expected
    assert d == d0


def test_expand():
    home = 'D:\\nx'
    add = '\\builds'
    s = '{HOME}' + add
    user_vars = {'HOME': home}
    assert nxconfig._expand(s, user_vars) == home + add
    s = '{UNDEFINED}' + add


def test_expand_invalid():
    s = '{DOESNOTEXIST}\\hello'
    user_vars = {'HOME': 'foo'}
    try:
        nxconfig._expand(s, user_vars)
    except KeyError as e:
        assert 'DOESNOTEXIST' == e.message
    else:
        assert False


def test_expand_project_no_rule():
    d0 = {'nx9': ['{REMOTE}/nx9', '{HOME}/nx9']}
    d = d0.copy()
    user_vars = {'REMOTE': 'foo', 'HOME': 'bar'}
    r = nxconfig._expand_project(d, user_vars)
    assert d == d0
    assert r['nx9'] == ['foo/nx9', 'bar/nx9']


def test_expand_project_missing_var():
    d = {'nx9': ['{FOO}', 'hello']}
    with pytest.raises(UserConfigInvalid):
        nxconfig._expand_project(d, {})


def test_expand_project_no_rule_invalid():
    d = {'nx10': ['{REMOTE}/nx10',]}
    user_vars = {'REMOTE': 'foo'}
    with pytest.raises(UserConfigInvalid):
        nxconfig._expand_project(d, user_vars)


def test_expand_project_with_rule():
    d = {
        'target_rule': '{HOME2}/{version}',
        'nx9': ['{REMOTE}/nx9', '{HOME}/nx9'],
        'nx10': ['{REMOTE}/nx10',]
    }
    user_vars = {'REMOTE': 'foo', 'HOME': 'bar', 'HOME2': 'cac'}
    r = nxconfig._expand_project(d, user_vars)
    assert r['nx9'] == ['foo/nx9', 'bar/nx9']
    assert r['nx10'] == ['foo/nx10', 'cac/nx10']


def test_is_frozen():
    assert nxconfig._is_frozen_remote('blahblah/ugii.exe')
    assert not nxconfig._is_frozen_remote('foo')


def test_expand_project_with_frozen_branch():
    d = {'nx9': ['something.exe', None]}
    assert nxconfig._expand_project(d, {}) == d
    d1 = {'nx9': ['something.exe', 'whocares']}
    assert nxconfig._expand_project(d1, {}) == d


def test_parse_config():
    d = {
        'foo': 'bar',
        'HOME': 'hello',
        'REMOTE': 'bye',
        'nx': {
            'target_rule': 'nx/{HOME}/{version}',
            'nx9': ['{REMOTE}/nx9/ugraf.exe', None],
            'nx10': ['{REMOTE}/nx10', None]
        },
        'tmg': {
            'target_rule': 'tmg/{HOME}/tmg{version}',
            'nx9': ['{REMOTE}/nx9'],
        }
    }
    r = nxconfig._parse_config(d)
    assert d == {}
    assert r.pop('foo') == 'bar'
    assert r.pop('nx') == {
        'nx9': ['bye/nx9/ugraf.exe', None],
        'nx10': ['bye/nx10', 'nx/hello/nx10']
    }
    assert r.pop('tmg') == {
        'nx9': ['bye/nx9', 'tmg/hello/tmgnx9']
    }
    assert r == {}


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


def test_can_read_default_config():
    nxconfig._read_default_config()


def test_read_user_config_error_not_found():
    fpath = 'doesnotexist'
    try:
        nxconfig._read_user_config(fpath)
    except UserConfigNotFound as e:
        assert fpath in e.message
    else:
        assert False


def test_read_user_config_invalid(tmpdir):
    tmp = str(tmpdir)
    fpath = os.path.join(tmp, 'config.json')
    open(fpath, 'w').write('{"tmg": {"first": 1 "second": 2}}')
    with pytest.raises(UserConfigInvalid):
        nxconfig._read_user_config(fpath)


def test_read_user_config(tmpdir):
    tmp = str(tmpdir)
    fpath = os.path.join(tmp, 'config.json')
    open(fpath, 'w').write('{"tmg": {"nx9": "Hello\\World"}}')


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
