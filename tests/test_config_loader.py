from src.core.yaml.config_yaml.config_yaml_loader import Config, ConfigYamlLoader
from src.support.types import Result
from src.librelnium.support.types import Locator
from logger import LogLevel
from typing import Any, get_args
import tests.vars as vars

def test_read(config_yaml: ConfigYamlLoader):
    yaml: dict[str, Any] = config_yaml.read(vars.BASE_CONFIG)
    
    res: Result[Config] = config_yaml.validate(yaml)

    assert not res.err

    data: Config = res.content

    assert data.auth_info and data.profile_url and data.settings

def test_default():
    config: Config = Config()

    assert config.auth_info.main_url == ""
    
def test_validate_default(config_yaml: ConfigYamlLoader):
    yaml: dict[str, Any] = config_yaml.read(vars.BASE_CONFIG)
    # this key has a default value defined with Config
    del yaml["auth_info"]["login_info"]["multi_page"]

    assert yaml.get("auth_info").get("login_info").get("multi_page") is None

    res: Result[Config] = config_yaml.validate(yaml)

    assert not res.err
    # default value is true
    assert res.content.auth_info.login_info.multi_page

def test_check_empty(config_yaml: ConfigYamlLoader):
    data: Config = Config()
    errors: list[str] = config_yaml.check_empty(dict(data))
    
    # second check is used in case recursive goes on for too long
    assert len(errors) > 0 and len(errors) < 20

def test_wrong_value_type(config_yaml: ConfigYamlLoader):
    raw: dict[str, Any] = config_yaml.read(vars.BASE_CONFIG)

    raw["profile_url"]["returns"] = 123
    raw["auth_info"]["main_url"] = True

    res: Result[Config] = config_yaml.validate(raw)

    assert not res.err and res.content.profile_url.returns == "" and res.content.auth_info.main_url == ""

def test_list_wrong_type(config_yaml: ConfigYamlLoader):
    raw: dict[str, Any] = config_yaml.read(vars.BASE_CONFIG)

    raw["auth_info"]["login_info"]["login_locators"] = True
    # checking if other values are not also changed
    base_url: str = raw["auth_info"]["main_url"]

    res: Result[Config] = config_yaml.validate(raw)
    assert not res.err

    arr: list[Any] = res.content.auth_info.login_info.login_locators

    assert len(arr) == 0 and res.content.auth_info.main_url == base_url

def test_wrong_id_literal(config_yaml: ConfigYamlLoader):
    raw: dict[str, Any] = config_yaml.read(vars.BASE_CONFIG)

    raw["auth_info"]["main_html_selector"] = True

    res: Result[Config] = config_yaml.validate(raw)
    assert not res.err

    assert res.content.auth_info.main_html_selector in get_args(Locator)

def test_wrong_log_literal(config_yaml: ConfigYamlLoader):
    raw: dict[str, Any] = config_yaml.read(vars.BASE_CONFIG)

    raw["settings"]["log_level"] = True

    res: Result[Config] = config_yaml.validate(raw)
    assert not res.err

    assert res.content.settings.log_level in get_args(LogLevel)