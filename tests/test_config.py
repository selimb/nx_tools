import nx_tools.api.config as nxconfig

def test_split_duplicates_no_input_modification():
    d0 = { 'nx10,nx1002':'a' }
    d = d0.copy()
    nxconfig._split_duplicates(d)
    assert d == d0

def test_split_duplicates_no_modification_needed():
    d = { 'nx10':'a', 'nx9':'b' }
    r = nxconfig._split_duplicates(d)
    assert r == d
