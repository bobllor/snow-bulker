from src.core.yaml.html_yaml.html_yaml_loader import HTMLYamlLoader
from src.core.yaml.html_yaml.types import HTMLFields
from src.support.types import Result
from typing import Any
from tests.vars import HTML_CONFIG

def test_read(html_yaml: HTMLYamlLoader):
    # surface reading, test_validate has deeper checks
    html_fields: HTMLFields = html_yaml.read(HTML_CONFIG)

    for key in HTMLFields.__annotations__:
        assert key in html_fields
    
def test_validate(html_yaml: HTMLYamlLoader):
    html_fields: dict[str, Any] = html_yaml.read(HTML_CONFIG)
    res: Result = html_yaml.validate(html_fields)

    assert not res.err and isinstance(res.content, HTMLFields)

def test_fail_validate(html_yaml: HTMLYamlLoader):
    html_fields: dict[str, Any] = html_yaml.read(HTML_CONFIG)

    del html_fields["return_fields"]["user"]

    res: Result = html_yaml.validate(html_fields)

    assert res.err and res.content is None