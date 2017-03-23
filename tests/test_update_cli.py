import pytest

from nx_tools.api import update as nxup
from nx_tools.cli import update as cliup

from .test_update import ftpstub, dev_7z, dummy_zip


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


def test_update_cli(dev_7z):
    '''Use mocked FTP, configuration and directories.
    Test 1) options (through parametrize?)
         2) Frozen/Untracked branches
         3) delete_zip
         4) sync/async?
    '''
    raise NotImplementedError
