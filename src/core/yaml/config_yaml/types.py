from pydantic import BaseModel, BeforeValidator
from src.librelnium.support.types import Locator
from logger import LogLevel
from typing import Annotated
import src.core.yaml.utils as utils


class ProfileUrl(BaseModel):
    '''URLs for the profiles.'''
    returns: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    custom: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    dell_i5: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    dell_i7: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    dell_i7_big: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""

class LoginElements(BaseModel):
    user_element: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    password_element: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    button_element: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""

class LoginInfo(BaseModel):
    login_locators: Annotated[list, BeforeValidator(utils.return_list)] = []
    login_elements: LoginElements = LoginElements()
    stay_signed_in_locator: Annotated[Locator, BeforeValidator(lambda v: utils.return_string(v, ""))] = "id"
    stay_signed_in_element: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    multi_page: Annotated[bool, BeforeValidator(lambda v: utils.return_bool(v, True))] = True

class AuthInfo(BaseModel):
    '''Holds the authentication information for the authentication process.'''
    main_url: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    main_html_attribute: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    main_html_selector: Annotated[Locator, BeforeValidator(lambda v: utils.return_literal(v, Locator, "id"))] = "id"
    url_substring: Annotated[str, BeforeValidator(lambda v: utils.return_string(v, ""))] = ""
    login_info: LoginInfo = LoginInfo()

class ProgramSettings(BaseModel):
    '''Used to hold the configuration of the program.'''
    headless: Annotated[bool, BeforeValidator(lambda v: utils.return_bool(v, False))] = False
    log_level: Annotated[LogLevel, BeforeValidator(lambda v: utils.return_literal(v, LogLevel, "info"))] = "info"

class Config(BaseModel):
    '''Class represaneting the config YAML file.'''
    auth_info: AuthInfo = AuthInfo()
    profile_url: ProfileUrl = ProfileUrl()
    settings: ProgramSettings = ProgramSettings()