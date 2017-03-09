import functools
import os

import pytest

import nx_tools


# TODO: Document this in CONTRIBUTING or something
def maya(reason):
    return pytest.mark.skipif(
        not os.environ.get('NX_TOOLS_ENV', '') == 'maya',
        reason=reason
    )


class VariableReturn(object):
    def __init__(self, answers):
        self.num_called = -1
        self.answers = answers

    def __call__(self, *args, **kwargs):
        self.num_called += 1
        return self.answers[self.num_called]

@pytest.fixture(scope='function')
def patch_prompt(monkeypatch):
    def wrapped(answers):
        stub = VariableReturn(answers)
        monkeypatch.setattr(nx_tools.cli._click, 'prompt', stub)

    return wrapped

