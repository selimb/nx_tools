import pytest

from nx_tools.cli import helpers

from .conftest import prompt_stub

dummy_items = ['foo', 'bar', 'baz']

@pytest.mark.parametrize('ans, expected', [
    ('a', range(len(dummy_items))),
    ('n', []),
    ('1', [1,]),
    ('1,2', [1,2]),
    ('0 2', [0,2])
])
def test_prompt_idx_range(prompt_stub, capfd, ans, expected):
    msg = 'Pick items.'
    prompt_msg = helpers._msg_range_fmt % msg
    options = helpers._mk_options(dummy_items)
    stub = prompt_stub([ans,])
    r = helpers.prompt_idx_range(dummy_items, msg)
    assert r == expected
    assert stub.validates()
    out, err = capfd.readouterr()
    expect_out = '\n'.join([options, prompt_msg]) + '\n'
    assert out == expect_out

    stub = prompt_stub(['-1', 'asd', '?', ans])
    r = helpers.prompt_idx_range(dummy_items, msg)
    assert r == expected
    assert stub.validates()
    out, err = capfd.readouterr()
    expect_out = '\n'.join([
        options,
        prompt_msg,
        helpers._invalid_idx_fmt % (len(dummy_items) - 1),
        options,
        prompt_msg,
        helpers._help_range,
        '',
        options,
        prompt_msg,
        helpers._help_range,
        '',
        options,
        prompt_msg
    ]) + '\n'
    assert out == expect_out

