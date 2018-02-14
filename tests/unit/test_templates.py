from mlt import templates


def test_template_list():
    table = templates.parse_templates()
    assert table is not None
