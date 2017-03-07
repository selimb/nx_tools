import functools
import os

import pytest

# TODO: Document this in CONTRIBUTING or something
def maya(reason):
    return pytest.mark.skipif(
        not os.environ.get('NX_TOOLS_ENV', '') == 'maya',
        reason=reason
    )

