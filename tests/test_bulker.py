from src.support.types import ExcelData
from src.core.bulker import Bulker, ProcessObject
from src.core.yaml.data_yaml.data_yaml_loader import DataYamlLoader
from src.core.yaml.html_yaml.html_yaml_loader import HTMLYamlLoader, HTMLFields
from src.core.yaml.yaml_loader import YamlLoader
from src.core.parser import Parser
from src.support.types import AddressData, CompanyData, UserData, Result, BulkData
from src.core.yaml.data_yaml.types import CustomOrder, DataYaml, RootData
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Any, Type
import tests.vars as vars
import src.support.utils as utils
import pandas as pd
import tempfile as tf
import os
import random

def write_email_cache(path: Path, amount: int = 5) -> list[str]:
    '''Writes to an email cache and returns the list of emails used to write.
    
    Parameters
    ----------
        path: Path
            The path to the cache file to write.
        
        amount: int
            The amount of emails to create. By default it will create 5 emails.
    '''
    if not path.parent.exists():
        path.parent.mkdir(exist_ok=True, parents=True)

    emails: list[str] = []
    for i in range(amount):
        val: int = i + 1

        emails.append(f"example.email{val}@domain.com")
    
    with open(path, "w") as file:
        for email in emails:
            file.write(email + "\n")
    
    return emails

def get_yaml_res(yaml_loader: Type[YamlLoader], file: Path | str) -> Result:
    yaml_raw: dict[str, Any] = yaml_loader.read(file, lower=True)
    res: Result = yaml_loader.validate(yaml_raw)

    return res

def copy_excel_files(root: Path) -> int:
    '''Copies the excel files to the given root folder. It returns
    the count of files that were copied over successfully.
    '''
    excels: list[Path] = [vars.EXCEL, vars.RETURN_EXCEL]
    count: int = 0

    for file in excels:
        out_path: Path = root / "output/data"

        if not out_path.exists():
            out_path.mkdir(parents=True, exist_ok=True)

        with open(file, "rb") as f1:
            content: str = f1.read()
        
            with open(out_path / file.name, "wb") as f2:
                f2.write(content)
                
                count += 1
    
    return count

@patch("src.core.driver_utils.DriverUtils.handle_dropdown")
@patch("src.core.bulker.os.replace")
def test_start(m1: MagicMock, m2: MagicMock, data_yaml: DataYamlLoader, html_yaml: HTMLYamlLoader, bulker: Bulker):
    config: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)

    # tested in a separate test
    del config["return"]

    res: Result = data_yaml.validate(config)
    assert not res.err

    root: RootData = res.content

    mock_driver: MagicMock = MagicMock()
    mock_webelement: MagicMock = MagicMock()
    mock_webelement.text.return_value = "Hello There"
    
    mock_driver.find_elements.return_value = [mock_webelement]

    mock_find_webelement: MagicMock = MagicMock()
    mock_driver.find_element.return_value = mock_find_webelement
    mock_find_webelement.find_elements.return_value = [mock_webelement]

    with open(vars.EXCEL, "rb") as f:
        bulker.check_project_files()
        data: bytes = f.read()

        with open(bulker.data_path / vars.EXCEL.name, "wb") as file:
            file.write(data)

    mock_profile_urls: MagicMock = MagicMock()
    bulk_data: Result[list[BulkData]] = bulker.get_bulk_data(root)

    raw: dict[str, Any] = html_yaml.read(vars.HTML_CONFIG, lower=True)
    html_res: Result[HTMLFields] = html_yaml.validate(raw)

    assert not html_res.err

    html_fields: HTMLFields = html_res.content

    bulker.start(bulk_data.content, html_fields, mock_profile_urls, driver=mock_driver, refresh=False)
    
    _, cache_path = bulker.get_cache("default_cache.txt")

    assert cache_path.exists() and len(bulker.failed_users) == 0

@patch("src.core.driver_utils.DriverUtils.handle_dropdown")
@patch("src.core.bulker.os.replace")
def test_return_start(m1: MagicMock, m2: MagicMock, data_yaml: DataYamlLoader, html_yaml: HTMLYamlLoader, bulker: Bulker):
    config: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)

    # tested in a separate test
    del config["normal"]

    res: Result = data_yaml.validate(config)
    assert not res.err

    root: RootData = res.content

    mock_driver: MagicMock = MagicMock()
    mock_webelement: MagicMock = MagicMock()
    mock_webelement.text.return_value = "Hello There"

    mock_find_webelement: MagicMock = MagicMock()
    mock_driver.find_element.return_value = mock_find_webelement
    mock_find_webelement.find_elements.return_value = [mock_webelement]

    with open(vars.EXCEL, "rb") as f:
        bulker.check_project_files()
        data: bytes = f.read()

        with open(bulker.data_path / vars.EXCEL.name, "wb") as file:
            file.write(data)

    mock_profile_urls: MagicMock = MagicMock()
    bulk_data: Result[list[BulkData]] = bulker.get_bulk_data(root)

    raw: dict[str, Any] = html_yaml.read(vars.HTML_CONFIG, lower=True)
    html_res: Result[HTMLFields] = html_yaml.validate(raw)

    assert not html_res.err

    html_fields: HTMLFields = html_res.content

    bulker.start(bulk_data.content, html_fields, mock_profile_urls, driver=mock_driver, refresh=False)
    
    _, cache_path = bulker.get_cache("default_cache.txt")

    assert cache_path.exists() and len(bulker.failed_users) == 0

def test_fail_get_bulk_data(bulker: Bulker, tmp_path: Path, data_yaml: DataYamlLoader):
    raw: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True) 

    raw["normal"]["data_file"] = "non-existent.xlsx"
    raw["return"]["data_file"] = "non-existent1.xlsx"

    res: Result[RootData] = data_yaml.validate(raw)

    assert not res.err

    copy_excel_files(tmp_path)

    bulk: Result[list[BulkData]] = bulker.get_bulk_data(res.content)

    assert len(bulk.content) == 0

def test_ignore_get_bulk_data(bulker: Bulker, tmp_path: Path, data_yaml: DataYamlLoader):
    raw: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)

    raw["normal"]["ignore"] = True

    res: Result[RootData] = data_yaml.validate(raw)

    assert not res.err

    copy_excel_files(tmp_path)

    bulk: Result[list[BulkData]] = bulker.get_bulk_data(res.content)

    assert len(bulk.content) == 1

def test_get_bulk(bulker: Bulker, tmp_path: Path, data_yaml: DataYamlLoader):
    res: Result[RootData] = get_yaml_res(data_yaml, vars.DATA_CONFIG)

    assert not res.err
    
    base_count: int = copy_excel_files(tmp_path)
    bulk: Result[list[BulkData]] = bulker.get_bulk_data(res.content)

    assert len(bulk.content) == base_count

def test_get_cache(tmp_path: Path, bulker: Bulker):
    file_name: str = "data.txt"
    file: Path = tmp_path / "output" / "cache" / file_name

    emails: list[str] = write_email_cache(file)

    (file.parent / "ex1.txt").touch()
    (file.parent / "ex2.txt").touch()
    emails2: list[str] = write_email_cache(file.parent / "folder5" / "ex3.txt", 10)
    emails3: list[str] = write_email_cache(file.parent / "folder1" / "folder2" / "ex1.txt", 7)

    bulker.check_project_files()

    # normal file in cache root
    cache_data: tuple[set[str], Path] = bulker.get_cache(file_name)
    cached_emails: set[str] = cache_data[0]
    cache_path: Path = cache_data[1]
    assert len(cached_emails) == len(emails) and cache_path.exists()

    # nested file
    cached_emails, cache_path = bulker.get_cache("ex3.txt")
    assert len(cached_emails) == len(emails2) and cache_path.exists()

    # duplicate file name, tests nested and a generic name (expect to get first matching file)
    # NOTE: this has to be explained in the docs
    cached_emails, cache_path = bulker.get_cache("folder2/ex1.txt")
    assert len(cached_emails) == len(emails3) and cache_path.exists()
    cached_emails, cache_path = bulker.get_cache("ex1.txt")
    assert len(cached_emails) == 0 and cache_path.exists()

    # file does not exist, the file and parents should be created
    no_file: str = "fdsafdsa.txt"
    cached_emails, cache_path = bulker.get_cache(no_file)
    assert len(cached_emails) == 0 and cache_path.exists()
    no_parent: str = f"folder15/{no_file}"
    cached_emails, cache_path = bulker.get_cache(no_parent)
    assert len(cached_emails) == 0 and cache_path.exists()

    # no file given, this should default to the default cache
    cached_emails, cache_path = bulker.get_cache()
    assert len(cached_emails) == 0 and cache_path.exists()

def test_write_cache(bulker: Bulker):
    bulker.check_project_files()

    cached_emails, cache_path = bulker.get_cache()

    base_cache: set[str] = cached_emails.copy()
    base_email: str = "test@email.com"

    cached_emails = bulker.add_to_cache(base_email, cached_emails, cache_path)

    new_emails, _ = bulker.get_cache()

    with open(cache_path, "r") as file:
        content: str = file.read().strip()

        assert content == base_email

    assert len(cached_emails) > len(base_cache) and cache_path.exists() and cached_emails == new_emails

def test_get_data(tmp_path: Path, bulker: Bulker):
    bulker.check_project_files()

    excel_file: Path = None
    temp_file: Path = None
    with tf.NamedTemporaryFile("wb", delete=False, delete_on_close=False, dir=tmp_path) as f1:
        with open(vars.EXCEL, "rb") as f2:
            excel_data = f2.read()
        
        f1.write(excel_data)
        temp_file = Path(f1.name)

        excel_file = bulker.data_path / f"{temp_file.name}.xlsx"
    
    os.replace(temp_file, excel_file)
    data: ExcelData | None = bulker.get_data(excel_file.name)

    assert data is not None

    rand_val: int = random.randint(0, len(data["address"][0]) - 1)

    df: pd.DataFrame = pd.read_excel(excel_file)

    rand_series: pd.Series = df.iloc[rand_val]
    base_set: set[str] = {str(val).lower() for val in rand_series}
    # lowering keys
    rand_series = rand_series.rename(lambda x: x.lower())
    rand_data: tuple[UserData, CompanyData, AddressData] = (
        data["user"][rand_val], data["company"][rand_val], data["address"][rand_val],
    )

    for data_set in rand_data:
        for key, val in data_set.items():
            val = str(val)
            if key not in ["desired by", "start date", "end date", "project id"]:
                if key in ["first name", "last name"]:
                    # first and last name columns are made, but the test file has a fullname column.
                    assert val in rand_series["full name"]
                elif key == "state":
                    # the state inside the test file can be an abbreviated or a full state
                    # it needs to be converted to the full state for the checks
                    state: str = utils.get_us_state(rand_series["state"])

                    assert state.lower() == val.lower()
                else:
                    # normal files, dates are skipped due to different formats.
                    # this is created with Parser.convert_date
                    assert val.lower() in base_set
            elif key == "project id":
                # the final p_id value has zeroes appended to it, the test file does not
                assert str(rand_series[key]) in val
            
def test_get_processes(bulker: Bulker, data_yaml: DataYamlLoader, parser: Parser):
    df: pd.DataFrame = parser.read(vars.EXCEL, add_years=1)

    user_data: list[UserData] = parser.get_user_data(df)
    address_data: list[AddressData] = parser.get_address_data(df)
    company_data: list[CompanyData] = parser.get_company_data(df)

    mock_processer: Mock = Mock()
    custom_order: CustomOrder = CustomOrder(
        cpu="intel i7",
        model="latitude",
        make="dell",
        ram=16,
        storage="256 gb"
    )
    data_yaml: DataYaml = DataYaml(
        account_manager_email="example@domain.com",
        profile="dell i7",
        data_file="some_data.xlsx",
        custom_order=custom_order,
    )
    

    processes: list[ProcessObject] = bulker.get_main_processes(
        mock_processer,
        user_data[0],
        company_data[0],
        address_data[0],
        data_yaml,
    )

    processes.extend(bulker.get_other_processes(mock_processer, data_yaml))

    for obj in processes:
        assert isinstance(obj["args"], tuple) and isinstance(obj["process_type"], str) and len(obj) == 3

def test_get_bulk_data(bulker: Bulker, data_yaml: DataYamlLoader):
    raw_yaml: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)
    res: Result[RootData] = data_yaml.validate(raw_yaml)

    assert not res.err

    root: RootData = res.content

    data_res: Result[list[BulkData]] = bulker.get_bulk_data(root)

    assert not data_res.err

    data: list[BulkData] = data_res.content

    assert len(data) > 0 and data[0].section == "normal"

@patch("src.core.process.DriverUtils.handle_dropdown")
def test_fail_users_start(_, data_yaml: DataYamlLoader, bulker: Bulker):
    raw: dict[str, Any] = data_yaml.read(vars.DATA_CONFIG, lower=True)
    res: Result[RootData] = data_yaml.validate(raw)

    assert not res.err

    data: RootData = res.content
    bulk_res: Result[list[BulkData]] = bulker.get_bulk_data(data)

    assert not bulk_res.err

    mock_html: Mock = Mock()
    mock_profile_urls: Mock = Mock()

    mock_element: Mock = Mock()
    mock_element.text = "John Doe"

    mock_driver: Mock = Mock()
    mock_driver.find_elements.return_value = [mock_element]

    bulker.start(bulk_res.content, mock_html, mock_profile_urls, driver=mock_driver)

def test_default_data_path(tmp_path: Path):
    bulker: Bulker = Bulker(tmp_path)
    bulker.check_project_files()

    root_dir: Path = bulker.project_path

    paths: list[Path] = [
        bulker.cache_path,
        bulker.data_path,
        bulker._log_path,
    ]

    for path in paths:
        assert path.exists()

def test_new_data_path(tmp_path: Path):
    data_path: Path = tmp_path / "some-data-folder-here"
    bulker: Bulker = Bulker(tmp_path, data_folder=data_path)

    bulker.check_project_files()

    assert data_path.exists() and data_path == bulker.data_path