import os

import pytest

# TODO: Document this in CONTRIBUTING or something
production = pytest.mark.skipif(
    not os.environ.get('NX_TOOLS_ENV', '') == 'prod',
    reason='Not a production environment.'
)
