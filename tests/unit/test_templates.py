from contextlib import contextmanager
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import sys
from mlt.commands.templates import Templates


@contextmanager
def catch_stdout():
    _stdout = sys.stdout
    sys.stdout = caught_output = StringIO()
    yield caught_output
    sys.stdout = _stdout
    caught_output.close()


def test_template_list():
    templates = Templates({'template': True, 'list': True})
    with catch_stdout() as caught_output:
        templates.action()
        assert caught_output.getvalue() is not None
