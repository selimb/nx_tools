import os
import pytest

import nx_tools.api as nxt
from nx_tools.constants import DEFAULT_CONFIG_PATH
from nx_tools.api import utils
from nx_tools.api.config import TRACKED, FROZEN, LOCAL


production = pytest.mark.skipif(
    not os.environ.get('NX_TOOLS_ENV', '') == 'prod',
    reason='Not a production environment.'
)

@pytest.fixture
def default_env():
    return nxt.config.Environment(DEFAULT_CONFIG_PATH)


@pytest.fixture
def check_defaults(default_env, tmpdir):
    def func(project_key):
        if project_key == 'tmg':
            updater_cls = nxt.update.TMGUpdater
            versions = default_env.list_tmg_versions()
            branches = [default_env.get_tmg_branch(ver) for ver in versions]
        elif project_key == 'nx':
            updater_cls = nxt.update.NXUpdater
            versions = default_env.list_nx_versions()
            branches = [default_env.get_nx_branch(ver) for ver in versions]
        else:
            raise AssertionError

        tmp = str(tmpdir)
        for i, branch in enumerate(branches):
            if branch.stat == LOCAL:
                continue
            if branch.stat == FROZEN:
                assert os.path.exists(branch.remote)
                continue
            local = os.path.join(tmp, str(i))
            up = updater_cls(local, branch.remote, False)
            new_items = up.list_new()
            assert new_items

    return func


@production
def test_tmg_defaults(check_defaults):
    check_defaults('tmg')


@production
def test_nx_defaults_exist(check_defaults):
    check_defaults('nx')


def test_default_config_no_errors(default_env):
    default_env.list_nx_versions()
    default_env.list_tmg_versions()
    default_env.get_tmg_branch('nx1101')
    default_env.get_nx_branch('nx12')


def test_can_parse_default_config():
    nxt.config._parse(utils.load_json(DEFAULT_CONFIG_PATH))
