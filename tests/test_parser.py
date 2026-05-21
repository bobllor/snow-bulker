from src.core.parser import Parser
from src.support.types import UserData, CompanyData, AddressData
from src.core.parser import ReturnColumns
from datetime import datetime
import tests.vars as vars
import src.support.utils as utils
import pandas as pd
import random
import re

DATE_REGEX: str = r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$"
DATE_COLUMNS: list[str] = ["Desired By", "Start Date", "End Date"]

def test_read(parser: Parser):
    # to be honest i have no idea what to assert here.
    # if this fails then exceptions will occur.
    df: pd.DataFrame = parser.read(vars.EXCEL, date_columns=DATE_COLUMNS, date_col_add_year="End_Date", add_years=1)

    assert "full name" in df.columns

def test_return_read(parser: Parser):
    df: pd.DataFrame = parser.read_return(vars.RETURN_EXCEL)

    for col in df.columns:
        low_col: str = col.lower()

        assert low_col == col

def test_get_return_data(parser: Parser):
    df: pd.DataFrame = parser.read_return(vars.RETURN_EXCEL)

    data: list[ReturnColumns] = parser.get_return_data(df)

    return_keys: list[str] = [key for key in ReturnColumns.__annotations__]
    # AddressData keys are also found in ReturnColumns
    address_keys: list[str] = [key for key in AddressData.__annotations__]

    keys: list[str] = return_keys + address_keys

    for di in data:
        for key in keys:
            assert di.get(key) is not None

def test_get_user_data(parser: Parser):
    df: pd.DataFrame = parser.read(vars.EXCEL, date_columns=DATE_COLUMNS, date_col_add_year="end date", add_years=1)

    data: list[UserData] = parser.get_user_data(df)

    user: UserData = data[random.randint(0, len(data) - 1)]
    user_keys: set[str] = {key for key in UserData.__annotations__}

    for key, val in user.items():
        assert key in user_keys and val != "" and isinstance(val, str)

    assert len(data) == len(df)

def test_get_address_data(parser: Parser):
    df: pd.DataFrame = parser.read(vars.EXCEL, date_columns=DATE_COLUMNS, date_col_add_year="end date", add_years=1)

    data: list[AddressData] = parser.get_address_data(df)

    address: AddressData = data[random.randint(0, len(data) - 1)]
    address_keys: set[str] = {key for key in AddressData.__annotations__}

    for key, val in address.items():
        if key == "state":
            assert val == utils.get_us_state(val)

        assert key in address_keys

    assert len(data) == len(df)

def test_address_data_postal_correction(parser: Parser):
    df: pd.DataFrame = parser.read(vars.EXCEL, date_columns=DATE_COLUMNS, date_col_add_year="end date", add_years=1)

    base_postals: list[str] = df["postal"].to_list()
    data: list[AddressData] = parser.get_address_data(df)

    for i, ad in enumerate(data):
        base_postal: str = base_postals[i]
        parsed_postal: str = ad["postal"]

        if "0" in parsed_postal:
            assert len(parsed_postal) == 5
        
        assert base_postal.replace(" ", "") in parsed_postal

def test_get_company_data(parser: Parser):
    df: pd.DataFrame = parser.read(vars.EXCEL, date_columns=DATE_COLUMNS, date_col_add_year="End_Date", add_years=1)

    data: list[CompanyData] = parser.get_company_data(df)

    company: CompanyData = data[random.randint(0, len(data) - 1)]
    company_keys: set[str] = {key for key in CompanyData.__annotations__}

    for key, val in company.items():
        # pid should include the leading four zeroes.
        if key == "p_id":
            assert len(val) >= 10

        assert key in company_keys

    assert len(data) == len(df)

def test_convert_date(parser: Parser):
    df: pd.DataFrame = pd.read_excel(vars.EXCEL)

    date_series: list[pd.Series] = [df[col] for col in DATE_COLUMNS]

    for series in date_series:
        data: pd.Series = parser.convert_date(series, add_years=10)

        for val in data:
            val_match: bool = re.fullmatch(DATE_REGEX, val) is not None

            assert val_match

def test_diff_time_convert_date(parser: Parser):
    df: pd.DataFrame = pd.read_excel(vars.EXCEL)
    series: pd.Series = df["Desired By"]

    series = series.apply(lambda x: datetime(2025, 1, 1, 12, 30, 55))

    data: pd.Series = parser.convert_date(series)

    for val in data:
        val_match: bool = re.fullmatch(DATE_REGEX, val) is not None

        assert val_match

def test_add_convert_date(parser: Parser):
    df: pd.DataFrame = pd.read_excel(vars.EXCEL)

    date_series: list[pd.Series] = [df[col] for col in DATE_COLUMNS]

    curr_year: int = datetime.now().year

    add_year: int = 10
    new_year: int = curr_year + add_year

    date_series[0] = date_series[0].apply(lambda x: "")

    data: pd.Series = parser.convert_date(date_series[0], add_years=10)

    for val in data:
        assert str(new_year) in val

def test_country_conversions(parser: Parser):
    df: pd.DataFrame = parser.read(vars.EXCEL)
    addr: list[AddressData] = parser.get_address_data(df)

    for ad in addr:
        assert ad["country"] in "United States" or ad["country"] in "Canada"