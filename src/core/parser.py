from src.support.types import UserData, AddressData, CompanyData, ReturnColumns
from typing import Any, Callable
from logger import Log
from pathlib import Path
from datetime import datetime, timedelta
import src.support.utils as utils
import pandas as pd

# these are the column names for the requestor, mapped to the internal
# variable names of the program.
# this is used so that requestors can "hopefully" type in the correct data
# and require less corrections in the data source.
DF_RETURN_COLUMNS: ReturnColumns = {
    "full name": "full name",
    "email": "email",
    "street": "street",
    "city": "city",
    "state": "state",
    "postal": "postal",
    "phone": "phone",
    "country": "country",
    "packaging required": "packaging required",
    "additional notes": "additional notes",
}

class Parser:
    '''Class used to read and parse the Excel data.'''
    def __init__(self, *, logger: Log = None):
        self.logger: Log = logger or Log()
    
    def read(self, file: Path | str | pd.DataFrame, 
    *, 
    date_columns: list[str] = ["desired by", "start date", "end date"], 
    date_col_add_year: str = "end date",
    date_fmt: str = None,
    add_years: int = 0) -> pd.DataFrame:
        '''Reads a given Excel path and parses the data, returning the DataFrame.
        The data will be cleaned and columns are formatted for internal usage.

        The DataFrame has lowercased keys and all values are converted into strings.

        If there is empty data then a ValueError is raised. KeyError can be raised if
        the keys in `date_columns` do not exist in the DataFrame columns.

        Parameters
        ----------
            file: PathStr | pd.DataFrame
                The Excel file, this can be a PathStr or the DataFrame.

            date_columns: list[str]
                The column names that represent the dates of the Excel. This is used to convert
                the dates to the format "YYYY-MM-DD" for ServiceNow. By default a list of three
                column names in the `headers.tsv` files are passed.
            
            date_col_add_year: str
                The date column name that will trigger adding the year to. This is used for missing dates
                in the DataFrame where a placeholder date is used instead, which is the current date.
                By default it uses the `end_date` column.
            
            date_fmt: str
                The format for the date. By default this is None, using "YYYY-MM-DD" as its default format.
                This should only be changed if ServiceNow changes the date requirement.
            
            add_years: int
                The amount of years to add to the date. This is only relevant if the original date is missing
                in the DataFrame, and the current date is used as its placeholder. This requires the
                column name of `date_col_add_year` to add the year to. By default it adds 0.
        '''
        if not isinstance(file, pd.DataFrame):
            file = Path(file)

        df: pd.DataFrame = pd.read_excel(file)

        # lowercase all keys
        df.rename(mapper=lambda x: x.strip().lower(), axis=1, inplace=True)
        date_columns = [col.lower() for col in date_columns]
        date_col_add_year = date_col_add_year.lower()

        df_columns: set[str] = {col for col in df.columns}

        if len(date_columns) > 0:
            for col in date_columns:
                if col not in df_columns:
                    raise KeyError(f"Missing date column {col} in file")

                series: pd.Series = df[col]

                if col == date_col_add_year:
                    df[col] = self.convert_date(series, fmt=date_fmt, add_years=add_years)
                else:
                    df[col] = self.convert_date(series, fmt=date_fmt)

        df = df.fillna('')

        def convert_raise_string(value: Any) -> str:
            new_val: str = str(value).strip()

            if new_val == "":
                raise ValueError(f"Empty value found in given file {file}")

            return new_val

        # convert all data to strings
        for col in df.columns:
            df[col] = self.apply(df, col, convert_raise_string)

        return df
    
    def read_return(self, file: Path | str | pd.DataFrame) -> pd.DataFrame:
        '''Reads a given Excel file and parses the data, returning the DataFrame.
        This is used only for parsing Return Excel files. The data will be cleaned and columns 
        are formatted for internal usage.

        The DataFrame has lowercased keys and all values are converted into strings.

        If the given file does not have the correct columns, a KeyError is raised.
        '''
        if not isinstance(file, pd.DataFrame):
            file = Path(file)

        df: pd.DataFrame = pd.read_excel(file)

        df.rename(lambda x: x.strip().lower(), axis=1, inplace=True)

        df = df.fillna("", axis=1)

        base_excel_columns: list[str] = [val.lower() for val in DF_RETURN_COLUMNS.values()]
        missing_cols: list[str] = self.validate_columns(df, base_excel_columns)

        if len(missing_cols) > 0:
            msg: str = f"Missing columns from Return Excel: {missing_cols}"
            self.logger.error(msg)

            raise KeyError(msg)

        return df
    
    def validate_columns(self, df: pd.DataFrame, columns: list[str]) -> list[str]:
        '''Validates the given DataFrame columns with a given baseline of columns. A list of
        missing columns will be returned, if any are missing.

        All values are converted to lower case by default.
    
        Parameters
        ----------
            df: DataFrame
                The DataFrame for validating.
            
            columns: list[str]
                A list of columns that are being checked if they exist in the DataFrame.
        '''
        missing_columns: list[str] = []
        df_cols: set[str] = {col.lower() for col in df.columns}
        columns = [col.lower() for col in columns]
        
        for col in columns:
            if col not in df_cols:
                missing_columns.append(col)

        return missing_columns
    
    def convert_date(self, data: pd.Series, *, fmt: str = None, add_years: int = 0) -> pd.Series:
        '''Converts a Series of pandas.Timestamp values to a string value. If the Series does not have
        a value that is of type pandas.Timestamp, then the next date from the current date will be used.

        The return Series are converted to a string.
        
        Parameters
        ----------
            data: pd.Series
                The Series containing pandas.Timestamp values.
            
            fmt: str
                The format string for the date. By default it is None and follows the format
                "YYYY-MM-DD".
            
            add_years: int
                Adds the number to the current date. This is only used if a value in the Series
                is not a pandas.Timestamp and the current date is used, in which case this adds
                a number to the current date. By default it is 0.
        '''
        # the date format will need to be changed as needed if ServiceNow changes it
        if fmt is None:
            fmt = "%Y-%m-%d"

        out: list[str] = []
        # check if there are invalid values
        data_list: list[pd.Timestamp | Any] = data.to_list()

        for val in data_list:
            if not isinstance(val, pd.Timestamp):
                curr_date: datetime = datetime.strptime(datetime.now().strftime(fmt), fmt)
                new_date: datetime = curr_date + timedelta(days=1)

                final_date: datetime = datetime(new_date.year + add_years, new_date.month, new_date.day)

                out.append(final_date.strftime(fmt)) 
            else:
                out.append(val.strftime(fmt))
    
        return pd.Series(out)
        
    def get_user_data(self, df: pd.DataFrame) -> list[UserData]:
        '''Gets the user data from the DataFrame.

        It returns a list of UserData dictionaries for each row in order.
        '''
        # read made this very easy. no need for other checks.
        data: list[UserData] = []
        user_keys: UserData = {key: key for key in UserData.__annotations__}

        for i in range(len(df)):
            user_data: UserData = {}
            row: pd.Series[str] = df.iloc[i]

            for key in user_keys:
                user_data[key] = row[key]

            data.append(user_data.copy())
        
        return data
    
    def get_address_data(self, df: pd.DataFrame) -> list[AddressData]:
        '''Gets the address data from the DataFrame.
        
        It returns a list of AddressData dictionaries for each row in order.

        A ValueError will be raised if the state is invalid, meaning it does not exist
        in both the United States and Canada.
        '''
        data: list[AddressData] = []
        address_keys: AddressData = {key: key for key in AddressData.__annotations__}

        for i in range(len(df)):
            address_data: AddressData = {}
            row: pd.Series[str] = df.iloc[i]

            for key in address_keys:
                value: str = row[key]

                # states have to be handled due to it often being an abberviation from requestors
                # postal has to be handled due to leading zeroes being dropped from Excel/pandas
                if key == address_keys["state"]:
                    # remove any periods or commas
                    value = value.replace(",", "").replace(".", "")

                    state: str = utils.get_us_state(value)

                    if state == "":
                        state = utils.get_canada_province(value)

                        if state == "":
                            self.logger.error(f"Invalid state/province given: {value}")
                            raise ValueError(f"Failed to find valid state/province with {value}") 

                    # final conversion to full state name 
                    value = state
                elif key == address_keys["postal"]:
                    # canada orders doesn't get effected by this, their postal is 6 or 7 characters long.
                    value = str(value)
                    zero_count: int = 5 - len(value)

                    if zero_count > 0:
                        zeroes: list[str] = ["0" for _ in range(zero_count)]

                        value = "".join(zeroes) + value
                    
                address_data[key] = value
            
            data.append(address_data.copy())
    
        return data
    
    def get_company_data(self, df: pd.DataFrame, *, leading_zeroes_pid: bool = True) -> list[CompanyData]:
        '''Gets the company data from the DataFrame.
        
        It returns a list of CompanyData dictionaries for each row in order. 

        Parameters
        ----------
            df: DataFrame
                The DataFrame from the Excel data.
            
            leading_zeroes_pid: bool
                Used to add leading zeroes to the project ID (PID). Due to Excel files and pandas trimming
                leading zeroes by default, there always is a minimum four leading zeroes.
        '''
        data: list[CompanyData] = []
        company_keys: CompanyData = {key: key for key in CompanyData.__annotations__}

        for i in range(len(df)):
            company_data: CompanyData = {}
            row: pd.Series[str] = df.iloc[i]

            for key in company_keys:
                value: str = row[key]
                
                if key == company_keys["project id"]:
                    # pids are either 10 or 11 characters long (i think)
                    # NOTE: may need to get more information on this.
                    if len(value) < 10:
                        zeroes_to_add: int = 10 - len(value)

                        zeroes: list[str] = ["0" for _ in range(zeroes_to_add)]

                        value = "".join(zeroes) + value

                company_data[key] = value

            data.append(company_data.copy())

        return data
    
    def get_return_data(self, df: pd.DataFrame) -> list[ReturnColumns]:
        '''Gets the return data from the DataFrame.
        
        It returns a list of ReturnColumns dictionaries for each row in order 
        of the DataFrame.
        '''
        # the initial elements will only consist of: full name, email, packaging, and additional notes
        data: list[ReturnColumns] = []
        keys: tuple[str] = (
            DF_RETURN_COLUMNS["full name"], 
            DF_RETURN_COLUMNS["email"], 
            DF_RETURN_COLUMNS["packaging required"],
            DF_RETURN_COLUMNS["additional notes"],
        )

        for i in range(len(df)):
            row: pd.Series[str] = df.iloc[i]

            temp_return: ReturnColumns = {}
            for key in keys:
                temp_return[key] = row[key]
        
            data.append(temp_return.copy())

        address_data: list[AddressData] = self.get_address_data(df)

        for i, add in enumerate(address_data):
            data[i].update(add)
        
        return data
    
    def apply(self, df: pd.DataFrame, col: str, func: Callable[[Any], Any]) -> pd.Series:
        '''Applies a function to a given column. It returns the same column as a Series
        with the function applied.
        '''
        series: pd.Series = df[col].apply(func=func)

        return series