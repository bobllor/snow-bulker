from src.core.yaml.data_yaml.data_yaml_loader import DataYamlLoader
from src.core.yaml.data_yaml.types import RootData, DataYaml
from src.support.types import Result
from typing import Any
import tests.vars as vars

def test_read(data_yaml: DataYamlLoader):
    yaml: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)
    res: Result = data_yaml.validate(yaml)

    assert not res.err

    data: RootData = res.content

    for key, cfg in data.root.items():
        assert key in yaml and len(dict(cfg)) > len(yaml[key])

def test_software_read(data_yaml: DataYamlLoader):
    yaml: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)
    res: Result[RootData] = data_yaml.validate(yaml)

    assert not res.err

    software_data: DataYaml = res.content.root["normal"]

    assert len(software_data.software) > 0
    
def test_check_default_read(data_yaml: DataYamlLoader):
    # any key from data.yml
    key: str = "normal"

    yaml: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)
    res: Result[RootData] = data_yaml.validate(yaml)
    data: DataYaml = res.content.root[key]

    default_values: list[Any] = [
        data.email_cache,
        data.hardware,
        data.software,
        data.ignore,
        data.desired_software,
        data.os_type,
        data.custom_order,
    ]

    assert all([val is not None for val in default_values])