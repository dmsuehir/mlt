from contextlib import contextmanager
from cStringIO import StringIO  # won't work in python3
import sys
from mlt.commands.templates import Templates


@contextmanager
def catch_stdout():
    _stdout = sys.stdout
    sys.stdout = caught_output = StringIO()
    yield caught_output
    sys.stdout = _stdout


def test_template_list():
    templates = Templates({'template': True, 'list': True})
    with catch_stdout() as caught_output:
        templates.action()
    assert caught_output is not None
