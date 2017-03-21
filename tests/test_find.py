import os

import pytest

from nx_tools.api import find

def test_find_ugraf(tmpdir):
    tmpdir.mkdir('foo')
    ugii = tmpdir.mkdir('UGII')
    ugraf = ugii.join('ugraf.exe')
    ugraf.write('')
    assert find.ugraf(str(tmpdir)) == str(ugraf)
    assert find.ugraf(str(ugii)) == str(ugraf)
    bar = tmpdir.mkdir('bar')
    ugraf2 = bar.mkdir('etc').mkdir('bin').join('ugraf.exe')
    ugraf2.write('')
    assert find.ugraf(str(bar)) == str(ugraf2)
    nope = tmpdir.mkdir('nope')
    nope.mkdir('foo')
    nope.mkdir('hello')
    nope.mkdir('UGII')
    assert find.ugraf(str(nope)) is None


def test_find_tmg(tmpdir):
    tmg_root = str(tmpdir.mkdir('foo'))
    assert find.tmg(tmg_root) is None
    tmg_root = tmpdir.mkdir('svn1234')
    tmg_root.mkdir('exe').join('MayaMonitor.exe').write('')
    assert find.tmg(str(tmg_root)) == str(tmg_root)
    tmg_root = tmpdir.mkdir('svn335')
    tmg_root.mkdir('tmg').mkdir('exe').join('MayaMonitor.exe').write('')
    assert find.tmg(str(tmg_root)) == os.path.join(str(tmg_root), 'tmg')

    # tmpdir.mkdir('svn1234').mkdir('

