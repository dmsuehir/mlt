from mlt.commands.templates import Template


def test_template_list():
    template = Template()
    assert template.template_list() is not None
