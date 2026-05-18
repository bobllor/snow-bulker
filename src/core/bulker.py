from logger import Log
from pathlib import Path
from src.librelnium.driver import Driver
from selenium.common.exceptions import InvalidArgumentException
from src.support.types import AddressData, CompanyData, UserData, ExcelData, Result, ReturnData, BulkData, UserInfo, BulkProfile
from src.core.yaml.data_yaml.types import CustomOrder
from src.core.parser import Parser, ReturnColumns
from src.core.process import ProcessFields
from src.core.yaml.data_yaml.types import RootData, DataYaml, AccountType
from src.core.yaml.html_yaml.types import HTMLFields
from src.core.yaml.config_yaml.types import ProfileUrl
from typing import Any, Callable, TypedDict
from threading import Event
import pandas as pd
import src.support.utils as utils
import tempfile as tf
import os

class ProcessObject(TypedDict):
    '''Object for the processor data for automation.'''
    func: Callable[[Any], Any]
    args: tuple[Any]
    process_type: str

class Bulker:
    '''Class for the bulking process.'''
    def __init__(self, 
            project_path: Path | str = None,
            *, 
            data_folder: Path | str = None,
            parser: Parser = None,
            logger: Log = None,
            event_flag: Event = None):
        '''Create a new Bulker.

        Parameters
        ----------
            project_path: Path | str
                The project PathStr of the data files. By default it is None and uses
                the root project directory where main.py is located.
            
            parser: Parser
                The parser for the Excel file, used to read and format the file into the
                expected data. By default it is None and uses a default Parser object.
            
            data_folder: Path | str
                The PathStr to the data folder. This is where the Excel files will be stored in.
                If the folder does not exist, then it will be created with its parents.
                By default it is None, using the project root directory.

            logger: Log
                The Log object. By default it is None and will output to stdout.
            
            event_flag: Event
                The threading Event flag. By default it is None.
        '''
        # only used if project_path is None
        project_root_path: Path = Path(__file__).parent.parent.parent
        if project_path is None:
            project_path = project_root_path

        self.project_path: Path = Path(project_path)
        if data_folder is None:
            data_folder = self.project_path / "data"

        self.logger: Log = logger or Log(log_path=project_root_path / "logs") 

        self.parser: Parser = parser or Parser(logger=self.logger)

        # excel data folder, this can be user defined or by default in root/output/data
        self._data_path: Path = Path(data_folder)

        # paths below cannot be changed, these will always be in the project root.
        # logs folder
        self._log_path: Path = self.logger.log_file.parent
        # email cache folder
        self._cache_path: Path = self.project_path / "output" / "cache"

        self._default_cache_file: str = "default_cache.txt"

        # file children list, these are set in method calls
        self._cache_children_paths: list[Path] = []
        self._data_children_paths: list[Path] = []

        self._failed_users: list[str] = []

        self._event_flag: Event = event_flag or Event()

    def start(self, 
    bulk_data: list[BulkData], 
    html_fields: HTMLFields,
    profile_urls: ProfileUrl,
    *, 
    timeout: float | int = 30,
    cart_delay: float | int = 3,
    driver: Driver = None,
    refresh: bool = True):
        '''Starts the bulking process.
        
        Parameters
        ----------
        bulk_data: list[BulkData]
            A list of BulkData objects containing the data used to start the
            automation process.
        
        html_fields: HTMLFields
            The data of the parsed HTML YAML file.

        timeout: float | int
            The time in seconds that is used for Driver wait time before causing a timeout exception.
            By default this is 30 seconds.

        cart_delay: float | int
            The waiting time in seconds after adding to cart.
        
        driver: Driver
            The Driver object for web automation via Selenium. By default it is None and
            will default to Chrome as the WebDriver.
        
        refresh: bool
            Boolean used to refresh the page *after* it gets added to cart. By default this is True.
        '''
        driver = driver or Driver("chrome")

        processor: ProcessFields = ProcessFields(driver, html_fields, logger=self.logger)

        for data in bulk_data:
            driver.set_wait_timer(timeout)
            if self._check_event():
                self.logger.info(f"Terminate process signal detected, exiting")
                return

            d_yaml: DataYaml = data.config
            if d_yaml.ignore:
                self.logger.info(f"Skipped section {data.section} (ignore is {d_yaml.ignore})")
                continue

            self.logger.info(f"Starting section {data.section}")

            url: str = utils.get_profile_url(d_yaml.profile, profile_urls)
            try:
                driver.go_to(url)
            except InvalidArgumentException:
                self.logger.error(f"Invalid URL '{url}' detected")
                continue

            # clear users before processing
            self._failed_users.clear()

            if data.profile == "normal": 
                self.logger.debug(f"Profile size (normal): {len(data.excel_data['address'])}")

                self.run_excel(
                    driver, 
                    processor, 
                    data.excel_data, 
                    yaml_data=d_yaml, 
                    email_cache=data.email_cache,
                    cache_file_path=data.cache_path,
                    url=url, 
                    refresh=refresh, 
                    cart_delay=cart_delay,
                    default_timeout=timeout,
                    section=data.section,
                )
            elif data.profile == "return":
                self.logger.debug(f"Profile size (return): {len(data.excel_data['return_data'])}")

                self.run_return(
                    driver,
                    processor,
                    data.excel_data,
                    account_manager_email=d_yaml.account_manager_email,
                    email_cache=data.email_cache,
                    cache_file_path=data.cache_path,
                    url=url,
                    refresh=refresh,
                    cart_delay=cart_delay,
                    default_timeout=timeout,
                    section=data.section,
                )
            else:
                self.logger.debug(f"Profile size (software): {len(data.excel_data["user"])}")

                self.run_software(
                    driver, 
                    processor, 
                    data.excel_data, 
                    yaml_data=d_yaml, 
                    email_cache=data.email_cache,
                    cache_file_path=data.cache_path,
                    url=url, 
                    refresh=refresh, 
                    cart_delay=cart_delay,
                    default_timeout=timeout,
                    section=data.section,
                )
            
        self._update_event()
    
    def run_software(self, 
        driver: Driver, 
        processor: ProcessFields, 
        excel_data: ExcelData,
        *,
        email_cache: set[str],
        yaml_data: DataYaml,
        cache_file_path: Path,
        url: str,
        refresh: bool,
        cart_delay: int | float,
        default_timeout: int,
        section: str = "",
        ) -> None:
        '''Runs the software Excel process.
        
        This shares similarities with the normal Excel process but does not use
        the address data.
        '''
        user_data: list[UserData] = excel_data["user"]
        company_data: list[CompanyData] = excel_data["company"]
        data_len: int = len(user_data)

        users_to_process: list[int] = self._get_users_to_process(user_data, email_cache)
        users_to_process_len: int = len(users_to_process)

        self.logger.info(f"Found {data_len - users_to_process_len}/{data_len} users in cache")

        if users_to_process_len == 0:
            self.logger.info(f"No orders to process")
            return

        for count, i in enumerate(users_to_process):
            if self._check_event():
                self.logger.info(f"Terminate process signal detected, exiting")
                return

            index: str = f"User {count + 1}"
            has_error: bool = False

            company: CompanyData = company_data[i]
            user: UserData = user_data[i]

            user_name: str = user["full name"]
            user_email: str = user["email"]
            if user_email in email_cache:
                continue

            processor.wait_for_page_load(
                "css selector", 
                processor.html_fields.company_fields.account_manager,
                7
            ) 

            self.logger.info(f"{index}: Starting user {user_name}")
            res: Result = processor.start_software_only_order(user, company, yaml_data.account_manager_email)
            if res.err:
                has_error = True
            
            driver.set_wait_timer(default_timeout)
            if has_error:
                self.logger.error(f"{index}: Failed to process order for {user_name}")
                self._failed_users.append(user_name)
                driver.go_to(url)
                continue
            
            add_res: Result = processor.add_to_cart(cart_delay)

            if not add_res.err:
                self.logger.info(f"{index}: User {user_name} created")
                email_cache = self.add_to_cache(user_email, email_cache, cache_file_path)
            else:
                self.logger.info(f"{index}: Failed to add {user_name} to cart")
                self.logger.error(f"{add_res.msg}, {add_res.content}")

            if refresh:
                driver.driver.refresh()

        self.log_failed_users(data_len, section)
    
    def run_excel(self, 
        driver: Driver, 
        processor: ProcessFields, 
        excel_data: ExcelData,
        *,
        email_cache: set[str],
        yaml_data: DataYaml,
        cache_file_path: Path,
        url: str,
        refresh: bool,
        cart_delay: int | float,
        default_timeout: int,
        section: str = "",
        ) -> None:
        '''Runs the normal Excel process.
        
        Parameters
        ----------
            driver: Driver
                The WebDriver.

            processor: ProcessFields
                The object used to start the automation process on the form with WebDriver.
            
            excel_data: ExcelData
                The parsed Excel data object. This is the standard Excel file for the Standard profiles.
            
            email_cache: set[str]
                The set of emails from the cache file.
            
            yaml_data: DataYaml
                The data YAML file containing the information for the form process.
            
            cache_file_path: Path
                The Path object to the cache file location.
            
            url: str
                The URL for the form page. This is used in case of errors and a full reset is needed.
            
            refresh: bool
                Used to refresh the page.
            
            cart_delay: int
                The timeout after adding to cart. This is recommended to be under 5 amount due to the
                notification disappearing in a short amount of time after adding to cart.
                If the notification does not disappear, then the amount of time is dependent on when
                API processing speeds.

            default_timeout: int
                The timeout for the page load. This is used for resetting the timeout back on each page load
                to reduce the timeout lock when the page is loaded but an element is not found.
        
            section: str
                The section name of the data YAML. By default it is an empty string.
        '''
        user_data: list[UserData] = excel_data["user"]
        company_data: list[CompanyData] = excel_data["company"]
        address_data: list[AddressData] = excel_data["address"]

        # clear users before a new run is started
        self._failed_users.clear()
        data_len: int = len(user_data)

        users_to_process: list[int] = self._get_users_to_process(user_data, email_cache)
        users_to_process_len: int = len(users_to_process)

        self.logger.info(f"Found {data_len - users_to_process_len}/{data_len} users in cache")

        if users_to_process_len == 0:
            self.logger.info(f"No orders to process")
            return

        self.logger.info(f"Processing orders for {users_to_process_len} user(s)")

        for count, i in enumerate(users_to_process):
            if self._check_event():
                self.logger.info(f"Terminate process signal detected, exiting")
                return
            curr_user: UserData = user_data[i]
            curr_company: CompanyData = company_data[i]
            curr_address: AddressData = address_data[i]

            index: str = f"User {count + 1}"
            user_name: str = curr_user["full name"]
            user_email: str = curr_user["email"].lower()
            if user_email in email_cache:
                continue
            
            processes: list[ProcessObject] = self.get_main_processes(
                processor,
                curr_user,
                curr_company,
                curr_address,
                yaml_data,
            )
            processes.extend(self.get_other_processes(processor, yaml_data))

            processor.wait_for_page_load(
                "css selector", 
                processor.html_fields.company_fields.account_manager,
                7
            ) 
            self.logger.info(f"{index}: Starting user {user_name}")
            has_error: bool = False
            for process in processes:
                res: Result = self.run_wrapper(process["func"], args=process["args"])

                if res.err:
                    self.logger.error(f"{res.msg} occurred during {process['process_type']}: {res.content}")
                    has_error = True
                    break

            driver.set_wait_timer(default_timeout)
            if has_error:
                self.logger.error(f"{index}: Failed to process order for {user_name}")
                self._failed_users.append(user_name)
                driver.go_to(url)
                continue
            
            add_res: Result = processor.add_to_cart(cart_delay)

            if not add_res.err:
                self.logger.info(f"{index}: User {user_name} created")
                email_cache = self.add_to_cache(curr_user["email"], email_cache, cache_file_path)
            else:
                self.logger.info(f"{index}: Failed to add {user_name} to cart")
                self.logger.error(f"{add_res.msg}, {add_res.content}")

            if refresh:
                driver.driver.refresh()
        
        failed_len: int = len(self.failed_users)
        if failed_len > 0:
            self.logger.warning(
                f"Failed {failed_len}/{data_len} users for section {section}" + \
                "\nUsers\n-----\n" + \
                "\n".join(self.failed_users)
            )
    
    def run_return(self,
        driver: Driver,
        processor: ProcessFields,
        excel_data: ReturnData,
        *,
        email_cache: set[str],
        account_manager_email: str,
        cache_file_path: Path,
        url: str,
        refresh: bool,
        cart_delay: int | float,
        default_timeout: int,
        section: str = "",
        ) -> None:
        '''Runs the return Excel process.
        
        Parameters
        ----------
        driver: Driver
                The WebDriver.

        processor: ProcessFields
            The object used to start the automation process on the form with WebDriver.
        
        excel_data: ReturnData
            The parsed Excel data object. This is the Return Excel file used for the Return profile.
        
        email_cache: set[str]
            The set of emails from the cache file.

        account_manager_email: str
            The account manager email of the user. This can be any value but it must exist in the ServiceNow
            database.
        
        cache_file_path: Path
            The Path object to the cache file location.
        
        url: str
            The URL for the form page. This is used in case of errors and a full reset is needed.
        
        refresh: bool
            Used to refresh the page.

        cart_delay: int
            The timeout after adding to cart. This is recommended to be under 5 amount due to the
            notification disappearing in a short amount of time after adding to cart.
            If the notification does not disappear, then the amount of time is dependent on when
            API processing speeds.

        default_timeout: int
            The timeout for the page load. This is used for resetting the timeout back on each page load
            to reduce the timeout lock when the page is loaded but an element is not found.
        
        section: str
            The section name of the data YAML. By default it is an empty string.
        '''
        return_data: list[ReturnColumns] = excel_data["return_data"]

        # clear users before a new run is started
        self._failed_users.clear()
        data_len: int = len(return_data)

        users_to_process: list[int] = self._get_users_to_process(return_data, email_cache)
        users_to_process_len: int = len(users_to_process)

        self.logger.info(f"Found {data_len - users_to_process_len}/{data_len} users in cache")

        if users_to_process_len == 0:
            self.logger.info(f"No orders to process")
            return

        self.logger.info(f"Processing orders for {users_to_process_len} user(s)")

        for count, i in enumerate(users_to_process):
            if self._check_event():
                self.logger.info(f"Terminate process signal detected, exiting")
                return
            obj: ReturnColumns = return_data[i]
            return_processes: list[ProcessObject] = self.get_return_processes(processor, obj, account_manager_email)

            user_name: str = obj["full name"]
            index: str = f"User {count + 1}"
            user_email: str = obj["email"].lower().strip()

            if user_email in email_cache:
                continue

            self.logger.info(f"{index}: Starting user {user_name}")
            has_error: bool = False

            processor.wait_for_page_load(
                "css selector", 
                processor.html_fields.company_fields.account_manager,
                7
            ) 
            for process in return_processes:
                res: Result = self.run_wrapper(process["func"], args=process["args"])

                if res.err:
                    self.logger.error(f"{res.msg} occurred during {process['process_type']}: {res.content}")
                    has_error = True
                    break

            driver.set_wait_timer(default_timeout)
            if has_error:
                self.logger.error(f"{index}: Failed to process return order for {user_name}")
                self._failed_users.append(user_name)
                driver.go_to(url)
                continue 
            
            add_res: Result = processor.add_to_cart(cart_delay)

            if not add_res.err:
                self.logger.info(f"{index}: User {user_name} created")
                email_cache = self.add_to_cache(user_email, email_cache, cache_file_path)
            else:
                self.logger.info(f"{index}: Failed to add {user_name} to cart")
                self.logger.error(add_res.msg, add_res.content)

            if refresh:
                driver.driver.refresh()

        failed_len: int = len(self.failed_users)
        if failed_len > 0:
            self.logger.warning(
                f"Failed {failed_len}/{data_len} users for section {section}" + \
                "\nUsers\n-----\n" + \
                "\n".join(self.failed_users)
            )

    def _get_users_to_process(self, data: list[UserInfo], email_cache: set[str]) -> list[int]:
        '''Parses the user data and looks for already used emails in the email cache, it will
        return a list of indices for users that do not have an entry in the cache for
        processing.
    
        Parameters
        ----------
            user_data: list[UserInfo]
                A list of UserInfo dictionaries. UserInfo contains
                the following two keys: `full name` and `email`.
        '''
        valid_users_indices: list[int] = []

        for i, user in enumerate(data):
            if user["email"].lower() in email_cache:
                continue

            valid_users_indices.append(i)

        return valid_users_indices
    
    
    def run_wrapper(self, func: Callable[[Any], Any], *, args: tuple[Any] = ()) -> Result:
        '''Runs a given function in a try-except block. A Result is returned.
        
        Parameters
        ----------
            func: Callable
                A function or method. This can accept any parameters and return any value.
            
            args: tuple[Any]
                A tuple of arguments to pass into the function. By default this is an empty
                tuple, meaning it will not pass any arguments.
        '''
        res: Result = Result(err=False, msg="Successful ran function")

        try:
            value: Result | None = func(*args) 

            if value is not None:
                if value.err:
                    return value
            else:
                self.logger.debug(f"Got None for value: {value}")
        except Exception as exc:
            self.logger.error("Unknown exception occurred during the process")
            res.err = True
            res.msg = exc

        return res
    
    def get_main_processes(self, 
        processor: ProcessFields,
        user_data: UserData, 
        company_data: CompanyData, 
        address_data: AddressData, 
        data_yaml: DataYaml
        ) -> list[ProcessObject]:
        '''Returns a list of ProcessObjects for running the main process in automating
        the ordering form.
        
        Parameters
        ----------
            processor: ProcessFields
                Object used to process the form fields on the page.

            user_data: UserData
                The user info from the Excel.
            
            company_data: CompanyData
                The company info from the Excel.
            
            address_data: AddressData
                The address info from the Excel.
            
            manager_email: str
                The email of the account manager.
            
            account_type: AccountType
                The account type of the project.
        '''
        processes: list[ProcessObject] = []

        if data_yaml.profile == "custom":
            processes.append(
                {
                    "func": processor.start_custom_fields,
                    "args": (data_yaml.custom_order,),
                    "process_type": "Custom Info"
                }
            )
        
        processes.append({
            "func": processor.start_user_fields,
            "args": (user_data,),
            "process_type": "User Info"
        })
        processes.append({
            "func": processor.start_company_fields,
            "args": (
                company_data, 
                data_yaml.account_manager_email,
                data_yaml.account_type,
                "global service" in company_data["operating company"].lower(), 
                data_yaml.waiver_file,
            ),
            "process_type": "Company Info"
        })
        processes.append({
            "func": processor.start_address_fields,
            "args": (address_data,),
            "process_type": "Address Info"
        })

        return processes
    
    def get_other_processes(self,
        processor: ProcessFields,
        data: DataYaml
        ) -> list[ProcessObject]:
        '''Returns a list of ProcessObjects for running the other processes,
        additional options for hardware, software, and operating system.
        
        Parameters
        ---------- 
        processor: ProcessFields
            Object used to process the form fields on the page.
        
        data: DataYaml
            The Excel data YAML information.
        '''
        processes: list[ProcessObject] = []

        processes.append({
            "func": processor.start_hardware_option_fields,
            "args": (data.hardware,),
            "process_type": "Hardware Info"
        })
        processes.append({
            "func": processor.start_software_option_fields,
            "args": (data.software,),
            "process_type": "Software Info"
        })
        processes.append({
            "func": processor.start_operating_system_fields,
            "args": (data.os_type,),
            "process_type": "OS Info"
        })
        processes.append({
            "func": processor.start_desired_software_option_fields,
            "args": (data.desired_software,),
            "process_type": "Desired Software Info"
        })

        return processes
    
    def get_return_processes(self, processor: ProcessFields, return_data: ReturnColumns, account_manager_email: str) -> list[ProcessObject]:
        processes: list[ProcessObject] = []

        processes.append({
            "func": processor.start_return_fields,
            "args": (return_data, account_manager_email,),
            "process_type": "Return Info"
        })

        return processes

    def check_project_files(self):
        '''Checks for the required project files existance and create them if missing.'''
        paths: list[Path] = [self._log_path, self._data_path, self._cache_path]

        for path in paths:
            if not path.exists():
                name: str = path.name
                parent: Path = path.parent

                self.logger.warning(f"Missing folder {name} in {parent}")

                path.mkdir(parents=True, exist_ok=True)

                self.logger.info(f"Created folder {name} in {parent}")

    def get_data(self, file: str, *, is_return_profile: bool = False, ignore_address: bool = False) -> ExcelData | ReturnData | None:
        '''Gets the data from the excel. This searches the `data` folder recursively.
        It will return a list of dictionaries ExcelData or ReturnData if `is_return_profile` is True. 

        If the file cannot be found, then None will be returned.
        
        Parameter
        ---------
            file: str
                The file name of the Excel file. This is expected to be either the file name, a 
                partial path, or the full path.
            
            is_return_profile: bool
                Indicates if the given file is a return Excel file. This will parse the Excel file 
                differently and will return `ReturnData` instead. By default this is False.
            
            ignore_address: bool
                Ignores all the columns related to address. If true, Data["address"] of the return value
                will be an empty array.
                This must be handled if true. By default it is false.
        '''
        data_path: Path = self._data_path / file
        if not data_path.parent.exists():
            data_path.mkdir(parents=True, exist_ok=True)
        
        if len(self._data_children_paths) == 0:
            self.logger.info("No data paths found, setting data paths")
            data_children: list[Path] = utils.get_path_files(self._data_path)

            self._data_children_paths = data_children
            self.logger.debug(f"Data children paths size: {len(data_children)}")
        
        if not data_path.exists():
            self.logger.info(f"Searching for {file} in the 'data' folder")
            for child in self._data_children_paths:
                child_lower: str = str(child).lower()

                # normalization for comparisons
                base_file: Path = Path(file)
                base_lower: str = str(base_file).lower()

                if base_lower in child_lower:
                    self.logger.info(f"Found file at {child.parent}")
                    data_path = child
                    break
        
        try:
            if not is_return_profile:
                df: pd.DataFrame = self.parser.read(data_path, add_years=1)

                address_data: list[AddressData] = []
                if not ignore_address:
                    address_data = self.parser.get_address_data(df)

                data: ExcelData = {
                    "address": address_data,
                    "company": self.parser.get_company_data(df),
                    "user": self.parser.get_user_data(df),
                }
            else:
                df: pd.DataFrame = self.parser.read_return(data_path)

                data: ReturnData = {
                    "return_data": self.parser.get_return_data(df)
                }
        except Exception as e:
            self.logger.error(f"Failed to parse Excel {data_path.name}:\n{e}")
            return None

        return data

    def get_cache(self, file: str = "") -> tuple[set[str], Path]:
        '''Retrieves the email cache from the cache folder as a set. If the file does not exist,
        then it will create the file. 
        
        A tuple of the emails in a hash set and the Path to the cache file will be returned.
        
        Parameter
        ---------
            file: str
                The file name of the cache file. By default it is an empty string, which if
                given the file will default to `default_cache.txt`.
        '''
        cache_path: Path = self._cache_path / file
        if not cache_path.parent.exists(): 
            cache_path.parent.mkdir(parents=True, exist_ok=True)

        if len(self._cache_children_paths) == 0:
            self.logger.info("No cache paths found, setting cache paths")
            cache_children: list[Path] = utils.get_path_files(self._cache_path)

            self._cache_children_paths = cache_children
            self.logger.debug(f"Cache children paths size: {len(self._cache_children_paths)}")

        if file == "": 
            self.logger.warning(f"No email cache found, defaulting to '{self._default_cache_file}'")
            cache_path = self._cache_path / self._default_cache_file
        elif not cache_path.exists():
            # search the cache children paths for the file, the file name must be contained in the paths
            # the docs will have to mention the parent path if duplicate names are used
            self.logger.info(f"Searching for {file} in the 'cache' folder")
            for cache in self._cache_children_paths:
                cache_str: str = str(cache).lower()
                # normalize path for comparisons
                base_file: Path = Path(file)
                lowered_file: str = str(base_file).lower()

                if lowered_file in cache_str:
                    self.logger.info(f"Found file at {cache.parent}")
                    cache_path = cache
                    break

        if not cache_path.exists():
            self.logger.info(f"{cache_path} not found, creating new file")
            cache_path.touch(exist_ok=True)

            return set(), cache_path

        data: list[str] = [] 
        with open(cache_path, "r") as f:
            data = f.readlines()

        data = [email.strip("\n").lower() for email in data]
        
        return set(data), cache_path
    
    def add_to_cache(self, email: str, cache: set[str], cache_path: Path) -> set[str]:
        '''Updates the cache with a new email entry and writes to the cache file. It returns
        a new copy of the cache.

        Parameters
        ----------
            email: str
                The email of the user.

            cache: set[str]
                The cache of emails of a user.
            
            cache_path: Path
                The Path to the cache file.
        '''
        cache_copy: set[str] = cache.copy()
        cache_copy.add(email)

        with tf.NamedTemporaryFile("w", delete=False) as file:
            if cache_path.exists():
                with open(cache_path, "r") as f:
                    file.write(f.read())
                    file.flush()
            
            file.write(email + "\n")

            temp_path: Path = Path(file.name)

        os.replace(temp_path, cache_path)
        
        return cache_copy
    
    def get_bulk_data(self, data: RootData) -> Result[list[BulkData]]:
        '''Returns a Result of BulkData for starting the bulking process.
        
        Parameters
        ----------
            data: RootData
                The RootData object, the dictionary from reading the data YAML file.
        '''
        out_bulk: list[BulkData] = []
        result: Result = Result(content=out_bulk)

        total_sections: int = len(data.root)
        failed: int = 0
        ignored: int = 0

        for section, cfg in data.root.items():
            self.logger.debug(f"Section {section} data: {cfg}")
            if cfg.ignore:
                self.logger.info(f"Skipped section {section} (ignore is {cfg.ignore})")
                ignored += 1
                continue
                
            # TODO: temp hardcode, change later for scalability
            is_software_order: bool = cfg.profile == "exchange"

            # return profile is a different excel type, but normal/software shares the same excel
            excel_data: ExcelData | ReturnData | None = self.get_data(
                cfg.data_file, 
                is_return_profile=cfg.profile == "return",
                ignore_address=is_software_order
            )
            if excel_data is None:
                self.logger.error(f"Failed to find Excel file {cfg.data_file}") 
                failed += 1
                continue
            
            email_cache, cache_path = self.get_cache(cfg.email_cache)
            self.logger.debug(f"Cache file: {cache_path.name} | Cache size: {len(email_cache)}")

            profile: BulkProfile = "normal"
            if cfg.profile == "return":
                profile = "return" 
            elif cfg.profile == "exchange":
                profile = "software"

            bulk_data: BulkData = BulkData(
                excel_data=excel_data,
                email_cache=email_cache,
                cache_path=cache_path,
                section=section,
                config=cfg,
                profile=profile
            )

            out_bulk.append(bulk_data)

        log_dict: dict[str, Any] = self.logger.create_dict(
            msg="Extracted Excel data from 'data.yml'", 
            total=total_sections,
            ignored=ignored,
            fails=failed,
        )

        result.msg = f"Data result: {log_dict}"
        result.err = failed == total_sections

        return result

    def log_failed_users(self, data_length: int, section: str) -> None:
        '''Logs the failed users to the WARNING level, if any.'''
        failed_len: int = len(self.failed_users)
        if failed_len > 0:
            self.logger.warning(
                f"Failed {failed_len}/{data_length} users for section {section}" + \
                "\nUsers\n-----\n" + \
                "\n".join(self.failed_users)
            )
    

    def _update_event(self):
        '''Updates the event to True. If it already is True, then this does nothing.''' 
        if not self._event_flag.is_set():
            self._event_flag.set()

        self.logger.info(f"Event flag update triggered: {self._event_flag.is_set()}")

    def _check_event(self) -> bool:
        '''Checks the event flag's status and return its status.'''
        return self._event_flag.is_set()

    @property
    def failed_users(self) -> list[str]:
        '''A list of users that failed during the automation process.'''
        return self._failed_users
    
    @property
    def cache_path(self) -> Path:
        return self._cache_path
    
    @property
    def data_path(self) -> Path:
        '''The data folder where the Excel files are expected to reside in.'''
        return self._data_path
    
    @property
    def default_cache_file(self) -> str:
        return self._default_cache_file