import os
import pytest

import nx_tools.api.config as nxconfig
from nx_tools.api import utils
from nx_tools.api.exceptions import InvalidConfig, NXToolsError


@pytest.fixture
def dummy_dct():
    return {
        'stuff': 'foo',
        'tmg': {
            'target_rule': 'tmg/{version}',
            'nx12': ['ftp/nx12',],
            'nx11': ['ftp/nx11', None],
            'dev': [None, 'dev/path'],
        },
        'nx': {
            'target_rule': 'nx/{version}',
            'nx12': ['remote/nx12',],
            'nx1101': ['remote/nx1101',],
            'nx1102': ['remote/nx1102', 'local/nx1102'],
            'nx9': ['nx9/to/ugii.exe', ],
            'nx8.5': ['path/to/ugii.exe', 'whatever']
        }
    }

@pytest.fixture
def dummy_env(dummy_dct, tmpdir):
    fpath = os.path.join(str(tmpdir), 'config.json')
    utils.write_json(dummy_dct, fpath)
    return nxconfig.Environment(fpath)


def test_environment_nx_branch(dummy_env, dummy_dct):
    for ver in ['nx12', 'nx1101', 'nx1102']:
        branch = dummy_env.get_nx_branch(ver)
        assert branch.stat == nxconfig.TRACKED
        assert branch.remote == 'remote/%s' % ver
        prefix = 'nx'
        if ver == 'nx1102':
            prefix = 'local'
        assert branch.local == '%s/%s' % (prefix, ver)
        assert dummy_env.get_branch(nxconfig.NX_KEY, ver) == branch
    for ver in ['nx9', 'nx8.5']:
        branch = dummy_env.get_nx_branch(ver)
        assert branch.stat == nxconfig.FROZEN
        assert branch.remote == dummy_dct['nx'][ver][0]
        assert branch.local == None
        assert dummy_env.get_branch(nxconfig.NX_KEY, ver) == branch
    with pytest.raises(NXToolsError):
        dummy_env.get_nx_branch('nx11')
        assert dummy_env.get_branch(nxconfig.NX_KEY, 'nx11') == branch
        dummy_env.get_nx_branch('nx15')
        assert dummy_env.get_branch(nxconfig.NX_KEY, 'nx15') == branch

def test_environment_tmg_branch(dummy_env):
    for ver in ['nx12', 'nx11']:
        branch = dummy_env.get_tmg_branch(ver)
        assert branch.stat == nxconfig.TRACKED
        assert branch.remote == 'ftp/%s' % ver
        assert branch.local == 'tmg/%s' % ver
        assert dummy_env.get_branch(nxconfig.TMG_KEY, ver) == branch
    assert dummy_env.get_tmg_branch('nx11') == dummy_env.get_tmg_branch('nx1101')
    branch = dummy_env.get_tmg_branch('dev')
    assert branch.stat == nxconfig.LOCAL
    assert branch.local == 'dev/path'
    assert branch.remote == None
    assert dummy_env.get_branch(nxconfig.TMG_KEY, 'dev') == branch


def test_config_list_versions(dummy_env):
    expect_tmg = set(['nx12', 'nx11', 'dev'])
    expect_nx = set(['nx12', 'nx1101', 'nx1102', 'nx9', 'nx8.5'])
    expects = [expect_tmg, expect_nx]
    funcs = ['list_tmg_versions', 'list_nx_versions']
    for func, expect in zip(funcs, expects):
        assert set(getattr(dummy_env, func)()) == expect


def test_config_get_option(dummy_env):
    assert dummy_env.get_option('stuff') == 'foo'
    with pytest.raises(NXToolsError):
        dummy_env.get_option('nope')
        dummy_env.get_option(nxconfig.TMG_KEY)
        dummy_env.get_option(nxconfig.NX_KEY)


def test_fuzzy_version_no_match():
    nx_version = 'nx10'
    available = ['nx9', 'nx11']
    with pytest.raises(NXToolsError):
        nxconfig.Environment._fuzzy_version(nx_version, available)


def test_fuzzy_version_ambiguous():
    nx_version = 'nx901'
    available = ['nx9', 'nx90', 'nx10']
    with pytest.raises(NXToolsError):
        nxconfig.Environment._fuzzy_version(nx_version, available)


def test_fuzzy_version_exact_match():
    nx_version = 'nx10'
    available = ['nx10', 'nx9']
    assert nxconfig.Environment._fuzzy_version(nx_version, available) == nx_version
    available.append('nx1001')
    assert nxconfig.Environment._fuzzy_version(nx_version, available) == nx_version


def test_fuzzy_version_fuzzy_match():
    nx_version = 'nx1001'
    available = ['nx9', 'nx10', 'nx11']
    assert nxconfig.Environment._fuzzy_version(nx_version, available) == 'nx10'


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
            'untracked': [None, '{HOME}/local'],
        }
    }
    r = nxconfig._parse(d)
    assert r.pop('foo') == 'bar'
    assert r.pop('nx') == {
        'nx9': ['bye/nx9/ugraf.exe', None],
        'nx10': ['bye/nx10', 'nx/hello/nx10']
    }
    assert r.pop('tmg') == {
        'nx9': ['bye/nx9', 'tmg/hello/tmgnx9'],
        'untracked': [None, 'hello/local']
    }
    assert r == {}


def test_parse_config_missing_project():
    d = {'stuff': 'foo'}
    with pytest.raises(InvalidConfig):
        nxconfig._parse(d)
    d['tmg'] = {'tmgstuff': 'foo'}
    with pytest.raises(InvalidConfig):
        nxconfig._parse(d)
    d['nx'] = {'nxstuff': 'bar'}
    nxconfig._parse(d)


def test_expand_project_with_untracked_branch():
    ver = 'dev'
    user_vars = {'HOME': 'myhome'}
    d = {ver: [None, '{HOME}/{version}/localdir']}
    expect = {ver: [None, 'myhome/%s/localdir' % ver]}
    assert nxconfig._expand_project(d, user_vars) == expect


def test_expand_project_error_on_version_in_remote():
    d = {'nx9': ['{version}/remote', 'foo']}
    with pytest.raises(InvalidConfig):
        nxconfig._expand_project(d, {})


def test_expand_project_with_frozen_branch():
    user_vars = {'REMOTE': 'rem'}
    remote = '{REMOTE}/something.exe'
    ver = 'nx9'
    d = {ver: [remote, None]}
    expect = {ver: ['rem/something.exe', None]}
    assert nxconfig._expand_project(d, user_vars) == expect
    d1 = {ver: [remote, 'whocares']}
    assert nxconfig._expand_project(d1, user_vars) == expect


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
    with pytest.raises(InvalidConfig):
        nxconfig._expand_project(d, {})


def test_expand_project_no_rule_invalid():
    d = {'nx10': ['{REMOTE}/nx10',]}
    user_vars = {'REMOTE': 'foo'}
    with pytest.raises(InvalidConfig):
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


def test_recursive_dict_update():
    d = {
        'tmg': {
            'default': 'tmgdefault',
            'nx9': 'a',
            'alist': [1, 2],
        },
        'default': 'blah',
        'override': None
    }
    u = {'tmg': {'nx9': 'b', 'alist': [5, 6]}, 'override': 'user'}
    r = nxconfig._recursive_dict_update(d, u)
    assert r['default'] == 'blah'
    assert r['override'] == 'user'
    assert r['tmg']['nx9'] == 'b'
    assert r['tmg']['default'] == 'tmgdefault'
    assert r['tmg']['alist'] == [5, 6]
