import pytest

import nx_tools.api.config as nxconfig
from nx_tools.api.exceptions import *

def test_split_duplicates_does_not_mutate_input():
    d0 = { 'nx10,nx1002':'a' }
    d = d0.copy()
    nxconfig._split_duplicates(d)
    assert d == d0

def test_split_duplicates_no_modification_needed():
    d = { 'nx10':'a', 'nx9':'b' }
    r = nxconfig._split_duplicates(d)
    assert r == d

def test_split_duplicates_full():
    keys = ['nx10', 'nx1001', 'nx1002']
    d = {}
    d[','.join(keys)] = 'a'
    d['nx9'] = 'b'
    expected = { 'nx9': 'b' }
    for k in keys:
        expected[k] = 'a'
    r = nxconfig._split_duplicates(d)
    assert expected == r

def test_split_duplicates_error_on_duplicate_entries():
    d = { 'nx9,nx10': 'a', 'nx10': 'b' }
    with pytest.raises(UserConfigInvalid):
        nxconfig._split_duplicates(d)
