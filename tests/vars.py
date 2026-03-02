from pathlib import Path

TEST_ROOT: Path = Path(__file__).parent

base_excel: str = "excel.xlsx"
return_excel: str = "return-excel-test.xlsx"

html_config: str = "test-html.yml"
data_config: str = "test-data.yml"
base_config: str = "test-config.yml"

excel_files: str = "excel-files"
config_files: str = "config-files"

BASE_CONFIG: Path = TEST_ROOT / config_files / base_config
DATA_CONFIG: Path = TEST_ROOT / config_files / data_config
EXCEL: Path = TEST_ROOT / excel_files / base_excel
RETURN_EXCEL: Path = TEST_ROOT / excel_files / return_excel
HTML_CONFIG: Path = TEST_ROOT /config_files / html_config