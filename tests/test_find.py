
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
    raise NotImplementedError

