import pytest
import os

# TODO: Document this in CONTRIBUTING or something
production = pytest.mark.skipif(
    not os.environ.get('NX_TOOLS_ENV', '') == 'prod',
    reason='Not a production environment.'
)

### # Finish this shit.
### @pytest.fixture(scope='function')
### def big_config():
###     '''Creates dummy configuration object along with temporary dummy directories
###
###     Configuration is returned through fixture.
###     '''
###     d = {
###         'local': {
###             'nx': {},
###             'tmg': {}
###         },
###         'remote': {
###             'nx': {},
###             'tmg': {}
###         }
###     }
###     local_root = tmpdir.mkdir('local')
###     local_dirs = {}
###     for nx_version in ('nx1003', 'nx11', 'nx1101'):
###         nx_root = local_root.mkdir(nx_version)
###         d['local']['nx'][nx_version] = nx_root.mkdir('builds')
###         d['local']['tmg'][nx_version] = nx_root.mkdir('patches')
###         local_dirs[n] = local_root.mkdir(n)
###     nx9_frozen = local_dirs['nx9'].join('ugraf.exe')
###     remote_root = tmpdir.mkdir('remote')
###     remote_dirs = {}
###     for n in ('nx1003', 'nx11', 'nx1101'):
###         remote_dirs[n] = remote_root.mkdir(n)
###
###     return Config({
###         'local': {
###             'NX': {
###                 'nx9': nx9_frozen,
###                 'nx1003': local_dirs['nx1003'].join('
