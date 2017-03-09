import pytest

from nx_tools.api import update as nxup
from nx_tools.cli import update as cliup
from .conftest import patch_prompt


def test_echo_result(capfd):
    item = 'foo'
    stat = nxup.TASK_SUCCESS
    reason = 'asdfa'
    r = nxup.TaskResult(item=item, stat=stat, reason=reason)
    cliup.echo_result(r)
    out, err = capfd.readouterr()
    assert out == 'Fetched %s.\n' % item
    stat = nxup.TASK_FAIL
    r = nxup.TaskResult(item=item, stat=stat, reason=reason)
    cliup.echo_result(r)
    out, err = capfd.readouterr()
    assert out == 'Error fetching %s.\n%s\n' % (item, reason)


def test_prompt_idx(patch_prompt, capfd):
    patch_prompt(['', '3', '1'])
    items = ['item1', 'item2']
    r = cliup.prompt_idx(items)
    print 'result0', r
    r = cliup.prompt_idx(items)
    print 'result1', r
    r = cliup.prompt_idx(items)
    print 'result2', r
    assert False

