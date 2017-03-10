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


class IterableReturnStub(object):
    def __init__(self, answers):
        self.num_called = 0
        self.answers = answers

    def __call__(self, *args, **kwargs):
        ret = self.answers[self.num_called]
        self.num_called += 1
        return ret

    def validates(self):
        return self.num_called == len(self.answers)


@pytest.fixture(scope='function')
def prompt_stub(monkeypatch):
    def wrapped(answers):
        stub = IterableReturnStub(answers)
        monkeypatch.setattr(nx_tools.cli._click, 'prompt', stub)
        return stub

    return wrapped

