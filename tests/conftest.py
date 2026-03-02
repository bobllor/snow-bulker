from src.core.bulker import Bulker
from src.core.parser import Parser
from src.core.process import ProcessFields
from src.core.yaml.html_yaml.html_yaml_loader import HTMLYamlLoader, HTMLFields
from src.core.yaml.data_yaml.data_yaml_loader import DataYamlLoader
from src.core.yaml.config_yaml.config_yaml_loader import ConfigYamlLoader
from src.support.types import Result
from pathlib import Path
from unittest.mock import MagicMock
from typing import Any
import tests.vars as vars
import pytest
import shutil

@pytest.fixture
def bulker(tmp_path: Path):
    bulker: Bulker = Bulker(project_path=tmp_path)
    bulker.check_project_files()

    shutil.copy(vars.EXCEL, bulker.data_path / vars.EXCEL.name)
    shutil.copy(vars.RETURN_EXCEL, bulker.data_path / vars.RETURN_EXCEL.name)

    yield bulker

@pytest.fixture
def parser():
    yield Parser()

@pytest.fixture
def html_yaml():
    yield HTMLYamlLoader()

@pytest.fixture
def data_yaml():
    yield DataYamlLoader()

@pytest.fixture
def config_yaml():
    yield ConfigYamlLoader()

@pytest.fixture
def processor():
    mock_driver: MagicMock = MagicMock()
    loader: HTMLYamlLoader = HTMLYamlLoader()

    raw: dict[str, Any] = loader.read(vars.HTML_CONFIG)
    res: Result[HTMLFields] = loader.validate(raw)

    yield ProcessFields(mock_driver, res.content)