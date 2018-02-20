from contextlib import contextmanager
try:
    # python 2
    from cStringIO import StringIO
except ImportError:
    # python 3
    # only supports unicode so can't be used in python 2 for sys.stdout
    # theory: `print` converts to `str` when appending newline, which it then
    # passes on to `sys.stdout.write`, throwing a type error
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
