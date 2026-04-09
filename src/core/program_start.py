from logger import Log
from src.librelnium.login import Login
from src.support.types import Result, BulkData
from src.core.yaml.config_yaml.types import LoginInfo, AuthInfo, Config
from src.core.yaml.yaml_loader import YamlStarter, ParsedYaml
from src.core.yaml.data_yaml.types import RootData
from src.core.yaml.html_yaml.types import HTMLFields
from src.core.bulker import Bulker
from src.librelnium.driver import Driver
from src.librelnium.login import LoginElements
from src.librelnium.support.types import Locator
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidArgumentException
from dotenv import load_dotenv
from pathlib import Path
from typing import Any
import src.support.utils as utils
import os
import time

class ProgramStarter:
    '''Class used to start and run the program.'''
    def __init__(self, project_root: Path, *, logger: Log = None):
        self.project_root: Path = project_root
        self.logger: Log = logger or Log()

        self._driver: Driver = None

    def start(self, 
    bulker: Bulker, 
    config: Config, 
    root_data: RootData, 
    html_fields: HTMLFields, 
    *, 
    headless: bool = False):
        '''Starting point for the program.

        Parameters
        ----------
            bulker: Bulker
                The Bulker object.

            config: Config
                The config YAML.

            root_data: RootData
                The data YAML.
            
            html_fields: HTMLFields
                The HTML YAML.
            
            headless: bool
                Run the driver in headless. By default it is False.
        '''
        bulk_res: Result[BulkData] = bulker.get_bulk_data(root_data)
        # any type of file reading error will cause err to be true, even if
        # correct files are parsed. this double checks for no files found.
        if bulk_res.err:
            self.logger.info(bulk_res.msg)
        if len(bulk_res.content) == 0:
            self.logger.info("No files were found")

            return

        # silent will be true, this cannot be changed.
        driver: Driver = Driver("chrome", wait_timer=5, options={"headless": headless, "silent": True})
        # used for turning off the driver in case of errors
        self._driver = driver
        login: Login = Login(driver.driver)
        
        try:
            driver.go_to(config.auth_info.main_url)
        except InvalidArgumentException:
            self.logger.error(f"Invalid URL '{config.auth_info.main_url}' detected")
            driver.quit()

            return

        login_res: Result = self.start_login(login, config.auth_info)
        if login_res.err:
            self.logger.error(login_res.msg)

            return

        # reset back to 11, start_login sets this to 3 during the login process 
        driver.set_wait_timer(11)
        bulker.start(
            bulk_res.content, 
            html_fields, 
            config.profile_url, 
            driver=driver,
            timeout=config.settings.timeout,
            wait_time=config.settings.refresh_timer
        )

    def start_login(self, login: Login, auth_info: AuthInfo) -> Result:
        '''Starts the login process. It returns a Result.
        
        Parameters
        ----------
            login: Login
                The Login driver.

            auth_info: AuthInfo
                The AuthInfo config parsed from the config YAML file.
        '''
        env_path: Path = self.project_root / ".env"

        result: Result = Result(msg="Successful login")
        login_info: LoginInfo = auth_info.login_info

        # temp_element is a random DOM element from the main site, if this is None then it is on
        # the login page
        random_dom: str = auth_info.main_html_attribute
        temp_element: WebElement | None = login.find_element(auth_info.main_html_selector, random_dom, return_none=True)

        if temp_element is None:
            login_elements: LoginElements = {
                "user_element": login_info.login_elements.user_element,
                "password_element": login_info.login_elements.password_element,
                "button_element": login_info.login_elements.button_element,
            }
            locators: list[Locator] = login_info.login_locators
            multi_page: bool = login_info.multi_page
            
            login_url: str = login.driver.current_url
            MAX_ATTEMPTS: int = 3
            attempts: int = 0

            username: str | None = None
            password: str | None = None
            url_substring: str = auth_info.url_substring

            if env_path.exists():
                load_dotenv()

                username = os.getenv("SN_USERNAME")
                password = os.getenv("SN_PASSWORD")

            for i in range(MAX_ATTEMPTS):
                failed_msg: str = f"Failed to login ({MAX_ATTEMPTS - (i + 1)} attempts left)"

                # mainly prevents an edge case where the login was successful
                # but the 
                if self._check_login(login, url_substring):
                    break

                try:
                    login.set_wait_timer(9)
                    login.login(
                        login_elements,
                        locators=locators,
                        multi_page=multi_page,
                        username=username,
                        password=password,
                    )

                    stay_signed_in_button: WebElement = login.find_element(
                        auth_info.login_info.stay_signed_in_locator,
                        auth_info.login_info.stay_signed_in_element,
                    )
                    stay_signed_in_button.click()

                    login.set_wait_timer(3)

                    if not self._check_login(login, url_substring):
                        self.logger.info(failed_msg)
                        login.go_to(login_url)
                        attempts += 1
                except Exception as e:
                    # TODO: test, i dont remember what errors occur here xdd
                    self.logger.error(e)
                    self.logger.info(failed_msg)

                    login.go_to(login_url)
                    attempts += 1
                    # required due to the speed of the next loop
                    time.sleep(.5)
                
                if attempts == MAX_ATTEMPTS:
                    result.msg = f"Failed to login to ServiceNow (max login attempts reached: {attempts})"
                    result.err = True

                    return result
            
        return result

    def parse_yaml(self, yaml_objs: list[YamlStarter], extensions: list[str]) -> Result[ParsedYaml]:
        '''Parses a list of `YamlStarter` and returns a Result.
        
        Parameters
        ----------
            yaml_objs: list[YamlStarter]
                A list of YamlStarter objects representing each YAML to parse.
            
            yaml_exts: list[str]
                A list of strings representing the YAML extenstions.
        '''
        p_yaml: ParsedYaml = {}
        result: Result[ParsedYaml] = Result(msg="Successfully parsed all YAML files", content=p_yaml)

        for obj in yaml_objs:
            file_path: Path | None = utils.get_file(self.project_root, obj["data_file"], exts=extensions, skip_dir=True)
            if file_path is None:
                msg: str =f"Missing '{obj["data_file"]}' YAML in {self.project_root}"
                self.logger.error(msg)
                result.err = True
                result.msg = "Errors occurred during YAML parsing"
                continue
                
            # config and HTML files are case sensitive, they must be lowered
            lower: bool = obj["parsed_key"] == "excel_root"
            raw_yaml: dict[str, Any] = obj["yaml_loader"].read(file_path, lower=lower)
            res: Result = obj["yaml_loader"].validate(raw_yaml)
            if res.err:
                return res

            result.content[obj["parsed_key"]] = res.content
        
        return result
    
    def quit_driver(self):
        '''Quits the Driver if it is not None.'''
        if self._driver is not None:
            self._driver.set_wait_timer(0)

            self._driver.quit()
            # reset for future method calls
            self._driver = None
        
    def _check_login(self, login: Login, url_substring: str) -> bool: 
        '''Checks the login page.'''
        if login.check_url(url_substring):
            return True
        
        return False