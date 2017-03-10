import pytest

from nx_tools.api import update as nxup
from nx_tools.cli import update as cliup


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

