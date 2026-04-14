from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from src.librelnium.driver import Driver
from src.librelnium.support.types import Locator
from src.core.driver_utils import DriverUtils, driver_wrapper
from src.support.types import CompanyData, UserData, AddressData, ReturnColumns
from src.core.yaml.data_yaml.types import CustomOrder, SoftwareOptions, HardwareOptions, OperatingSystems, AccountType
from src.core.yaml.html_yaml.types import HTMLFields, AddressFields, ClientFields, AddonFields, CompanyFields
from src.core.yaml.html_yaml.types import ReturnFields, CustomHardwareFields
from src.support.types import Result
from typing import Callable, Any
from logger import Log
from datetime import datetime
from pathlib import Path
import src.support.utils as u

class ProcessFields:
    '''Class to automate processing the fields of the ordering form. The core fields methods will require data
    retrieved from parsing the Excel file. The optional fields and custom fields are obtained from the configuration YAML
    file. 
    
    The methods in the class are divided into different sections that matches the ordering form from
    top to bottom. The following sections are:
    1. Client fields (from Full name to Employee ID)
    2. Company fields (from Operating company to Street 1)
    3. Address fields (from Street 1 to Phone No)
    4. Optional fields: Peripherals, software, and OS information
        - Hardware fields
        - Operating system field
        - Software fields
        - Desired software field

    Custom fields: ***Only applicable if using the Custom Hardware form*** (from Make to Other hardware specifications).
    This is will be above client fields if the "Profile" config value is `custom`. All the other fields remain the same
    after this section.

    Return Excel files only need to have one method call, `start_return_fields`. It is a small page and only applies to
    existing users, which eliminates a huge chunk of the initial setup. The address fields also exist in the return page,
    but is handled within the same method call.
    
    Due to the nature of WebView, JavaScript, and web automation, there will be errors raised if issues occur. It is
    *recommended to wrap method calls in a try-except block* in order to properly handle errors.
    
    Errors typically occurs on *drop-down menus*. When a drop-down is active it takes precedent over other elements. 
    This often causes blocks when attempting to access other elements underneath if not properly closed out.

    ***IMPORTANT***: If the developers of ServiceNow ever decides to change the structure of the form, then both the
    fields coded within the class and the method call order *are subject to change*.
    '''
    def __init__(self, driver: Driver, html_fields: HTMLFields, *, logger: Log = None):
        '''
        Parameters
        ----------
            driver: Driver
                The WebDriver.
            
            html_fields: HTMLFields
                The HTMLFields data to automate and target the fields on the form.
            
            logger: Log
                The Log object for logging. By default it is None and uses default settings.
        '''
        self.driver: Driver = driver
        self.utils: DriverUtils = DriverUtils(driver)

        self.html_fields: HTMLFields = html_fields

        self.logger: Log = logger or Log()

    @driver_wrapper 
    def start_address_fields(self, address_data: AddressData, res: Result = None) -> Result:
        '''Starts the address fields automation.

        This is the 3rd section of the normal ordering page.
        
        Parameters
        ----------
            address_data: AddressData
                A dictionary that holds the address data information.

        res: Result
            The Result of the method call. This should be left empty for the decorator
            to pass as an argument. By default it is None    
        '''
        if res is None:
            res = Result()
        res.msg = "Current process: Address Fields"

        self.logger.debug(f"Address data: {address_data}")
        # country and state requires special interactions due to them being a drop down element.
        fields: AddressFields = self.html_fields.address_fields
        address_values: dict[str, str] = {
            "street": fields.street,
            "city": fields.city, 
            "country": fields.country,
            "state": fields.state, 
            "postal": fields.postal,
            "phone": fields.phone,
        }

        dropdowns: set[str] = {"state", "country"}

        for key, field in address_values.items():
            element: WebElement = self.utils.get_element_css(field)

            res.content = self.get_res_content(key, field)
            if key in dropdowns:
                self.utils.handle_dropdown(value=element, key=address_data[key], send_enter=True)
                continue

            if not element.is_displayed():
                self.driver.action_driver.scroll_to_element(element)

            self.utils.clear_field(element)
            self.driver.action_driver.send_keys_to_element(element, address_data[key]).perform()

        return res

    @driver_wrapper   
    def start_user_fields(self, user_data: UserData, res: Result = None) -> Result:
        '''Starts the fields to create the user.

        This is the 1st section of the normal ordering page. If an element is not found, a
        NoSuchElementException is raised.
        
        Parameters
        ----------
            user_data: UserData
                A dictionary that holds the user data information.
            
            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("User fields")

        fields: ClientFields = self.html_fields.client_fields
        self.logger.debug(f"User data: {user_data}")

        res.content = self.get_res_content("username", fields.name)
        self.utils.handle_dropdown(value=fields.name, key=user_data["email"])

        no_users: str = "No matches found"
        res.content = self.get_res_content("usernames list", fields.name_list)
        users_list: list[WebElement] = self.driver.find_elements("css selector", fields.name_list)

        # by default if no users are found, the string "no matches found" is seen.
        # if this doesn't exist, either the wrong attribute is used or it got changed.
        if len(users_list) == 0: 
            self.logger.warning(f'Could not find element for "Full name" entry {fields.name_list}')
            res.err = True

            return res

        # checks if the user exists before filling the information
        user_exist: bool = users_list[-1].text.lower() != no_users.lower()
        if not user_exist:
            self.driver.send_keys(Keys.ESCAPE, pause=.3)

            res.content = self.get_res_content("user not found button", fields.not_found_button)
            user_not_found_button: WebElement = self.driver.find_element("css selector", fields.not_found_button)
            self.driver.click(user_not_found_button, pre_pause=.1)

            name_split: list[str] = user_data["full name"].split()
            first_name: str = name_split[0]

            last_name: str = name_split[-1]
            if len(name_split) > 2:
                last_name = " ".join(name_split[1:])

            user_info: list[tuple[str, str]] = [
                (fields.first_name, first_name),
                (fields.last_name, last_name),
                (fields.email, user_data["email"]),
            ]
            keys: list[str] = ["first name", "last name", "email"]
            for i, field in enumerate(user_info):
                user_field: str = field[0]
                user_str: str = field[-1]
                key: str = keys[i]

                res.content = self.get_res_content(key, user_field)
                element: WebElement = self.driver.find_element("css selector", user_field)

                element.send_keys(user_str)
        else:
            # skips the dropdown selection by directly adding the value in.
            # this also autofills the other information for the user.
            self.driver.send_keys(Keys.ENTER, pause=.3)

        res.content = self.get_res_content("employee id", fields.employee_id)
        e_id_element: WebElement = self.driver.find_element("css selector", fields.employee_id)
        # whatever info is given in user_data will
        # take precedent over the one stored in the database.
        self.utils.clear_field(e_id_element)
        e_id_element.send_keys(user_data['employee id'])

        return res

    @driver_wrapper 
    def start_desired_software_option_fields(self, desired_software: str = "", res: Result = None) -> Result:
        '''Starts the process for the desired software option. This handles software requests that
        do not have an option/checkbox by default by utilziing the text field.

        This is the 4th section of the normal ordering page.

        Parameters
        ----------
            desired_software: str, default ""
                The desired software, this is the value used to fill the field. By default it is an empty string and
                will not run.
            
            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("Desired Software")

        fields: AddonFields = self.html_fields.addon_fields
        if desired_software != "":
            self.logger.debug(f"Desired software: {desired_software}")
            res.content = self.get_res_content("software not listed", fields.software_not_listed)
            not_listed_element: WebElement = self.driver.find_element("css selector", fields.software_not_listed)
            not_listed_element.click()

            res.content = self.get_res_content("desired software", fields.desired_software)
            desired_software_element: WebElement = self.driver.find_element("css selector", fields.desired_software)
            desired_software_element.send_keys(desired_software)
        
        return res

    @driver_wrapper  
    def start_software_option_fields(self, software_list: list[SoftwareOptions], res: Result = None) -> Result:
        '''Starts the software option fields. 
        
        This is the 4th section of the normal ordering page.
        
        Parameters
        ----------
            software_list: list[str]
                A list of software options. The list is expected to contain the strings found
                in SoftwareOptions. If in invalid option is given, then it will return a
                Result error.
            
            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("Software Options")
        
        fields: AddonFields = self.html_fields.addon_fields

        if len(software_list) > 0:
            self.logger.debug(f"Software list: {software_list}")

            # these are HTML options.
            # they have underscores from the schema, it must be replaced
            # in order for the software_list elements to check properly
            # NOTE: there are two SoftwareOptions in 'HTML'and 'data' YAML that need to match... sorry in advance.
            software_options: dict[str, str] = {key.replace("_", " "): val for key, val in dict(fields.software).items()}

            for software in software_list:
                software = software.lower()

                if software not in software_options:
                    err_msg: str = f"Entry {software} is not a valid option"
                    
                    res.content = err_msg
                    res.err = True
                    
                    return res

                element_id: str = software_options[software]

                res.content = self.get_res_content(software, element_id)
                element: WebElement = self.driver.find_element("css selector", element_id)
                element.click()
    
        return res

    @driver_wrapper 
    def start_hardware_option_fields(self, hardware_list: list[HardwareOptions], res: Result = None) -> Result:
        '''Starts the hardware option fields. 
        
        This is the 4th section of the normal ordering page.
        
        Parameters
        ----------
            hardware_list: list[str]
                A list of hardware options. The list is expected to contain the strings found
                in HardwareOptions. If in invalid option is given, then it will return a
                Result error.
            
            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("Option Fields")

        fields: AddonFields = self.html_fields.addon_fields

        if len(hardware_list) > 0:
            self.logger.debug(f"Hardware list: {hardware_list}")

            # same issue as start_software_option_fields.
            hardware_options: dict[str, str] = {key.replace("_", " "): val for key, val in dict(fields.hardware).items()}

            for hardware in hardware_list:
                hardware = hardware.lower()

                if hardware not in hardware_options:
                    err_msg: str = f"Entry {hardware} is not a valid option"
                    
                    res.content = err_msg
                    res.err = True
                    
                    return res

                element_id: str = hardware_options[hardware]

                res.content = self.get_res_content(hardware, element_id)
                element: WebElement = self.driver.find_element("css selector", element_id)
                element.click()
        
        return res

    @driver_wrapper 
    def start_company_fields(self, 
        company_data: CompanyData, 
        account_manager_email: str, 
        project_account_type: AccountType = "regional",
        require_region: bool = False,
        waiver_file: str = "",
        res: Result = None) -> Result:
        '''Starts the company field operations.

        This is the 2nd section of the normal ordering page.

        Parameters
        ----------
            company_data: CompanyData
                A dictionary consisting of the CompanyData of the Excel file.
            
            account_manager_email: AccountType
                The email of the account manager. This is the manager of the user, and can either be the
                actual manager or a requestor/point of contact. Obtained from the YAML configuration.

            project_account_type: AccountType
                The account type of the project. This is only used if the operating company contains "staffing",
                otherwise it will be unused. By default it is "regional".
            
            require_region: bool
                Flag used to handle the Sales Region drop down. This is required to be True if the *operating company*
                is Global Services, any other value does not require this. By default it is False.
            
            waiver_file: str
                The waiver file name, this must include the extension. If a waiver file is included, then it will trigger
                a new waiver workflow that adds the waiver to the input file. By default it is an empty string.

            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("company fields")
        
        fields: CompanyFields = self.html_fields.company_fields
        self.logger.debug(f"Company data: {company_data}")

        res.content = self.get_res_content("operating company", fields.operating_company)
        self.utils.handle_dropdown(value=fields.operating_company, key=company_data["operating company"], send_enter=True, wait_time=.8)

        pid: str = company_data["project id"]
        res.content = self.get_res_content("project id", fields.project_id)
        self.utils.handle_dropdown(value=fields.project_id, key=pid, send_enter=True, wait_time=.8)

        res.content = self.get_res_content("division", fields.division)
        div_element: WebElement = self.driver.find_element("css selector", fields.division)
        if div_element.get_attribute("value").strip() == "":
            div_element.send_keys(company_data["division"])

        if require_region:
            res.content = self.get_res_content("region", fields.region)
            self.utils.handle_dropdown(value=fields.region, key=company_data["region"], send_enter=True, wait_time=.8)

        # honestly not sure what this is but it's never used. will always be no.
        res.content = self.get_res_content("sub vendor", fields.sub_vendor)
        self.utils.handle_dropdown(value=fields.sub_vendor, key="No", send_enter=True, send_down=True, wait_time=.8)
        res.content = self.get_res_content("account_manager", fields.account_manager)
        self.utils.handle_dropdown(
            value=fields.account_manager, 
            key=account_manager_email, 
            send_tab=True, 
            wait_time=.5,
            post_wait=1,
        )

        runners: list[tuple[Callable[[Any], Result], tuple[Any]]] = [
            (self.company_fill_dates, (company_data, fields,),),
            (self.company_fill_company, (company_data, fields,),),
        ]
        for tup in runners:
            func = tup[0]
            args = tup[-1]

            comp_res: Result = func(*args)

            if comp_res.err:
                return comp_res

        # NOTE: this is a new feature added by SNOW devs... staffing is required to have this.
        # i am unsure if this is permanent or a mistake.
        if "staffing" in company_data["operating company"].lower():
            res.content = self.get_res_content("project account type", fields.account_type)
            self.utils.handle_dropdown(value=fields.account_type, key=project_account_type, send_enter=True, wait_time=.8)
            res.content = self.get_res_content("regional sub account", fields.regional_sub_account)
            self.utils.handle_dropdown(
                value=fields.regional_sub_account, 
                key=company_data["region"], 
                send_enter=True, 
                send_down=True, 
                wait_time=.8
            )

        # NOTE: the key will be new device as a new order will always be a new device.
        res.content = self.get_res_content("request type", fields.request_type)
        self.utils.handle_dropdown(value=fields.request_type, key="New device", send_tab=True, wait_time=1)
        # NOTE: not used. they have to manually add these themselves as this requires special permissions
        # from higher up management.
        res.content = self.get_res_content("admin", fields.admin)
        self.utils.handle_dropdown(value=fields.admin, key="No", send_enter=True, send_down=True, wait_time=.8)
        res.content = self.get_res_content("universal serial bus storage", fields.usb)
        self.utils.handle_dropdown(value=fields.usb, key="No", send_enter=True, send_down=True, wait_time=.8)

        if waiver_file != "":
            waiver_res: Result = self.upload_waiver(waiver_file)
            if waiver_res.err:
                return waiver_res

        return res

    @driver_wrapper
    def start_custom_fields(self, custom_data: CustomOrder, res: Result = None) -> Result:
        '''Starts the custom order fields. This is necessary if the `profile` field
        in the YAML configuration is `custom`.

        This is the 1st section of custom order/hardware ordering page. It does not exist
        in the normal ordering page.

        Parameters
        ----------
            custom_data: CustomOrder
                The custom hardware data of the profile in the data YAML.
            
            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("custom field")

        fields: CustomHardwareFields = self.html_fields.custom_fields
        self.logger.debug(f"Custom data: {custom_data}")

        res.content = self.get_res_content("make", fields.make)
        make_element: WebElement = self.driver.find_element("css selector", fields.make)
        make_element.send_keys(custom_data.make)

        res.content = self.get_res_content("model", fields.model)
        model_element: WebElement = self.driver.find_element("css selector", fields.model)
        model_element.send_keys(custom_data.model)

        res.content = self.get_res_content("storage", fields.storage)
        storage_element: WebElement = self.driver.find_element("css selector", fields.storage)
        storage_element.send_keys(custom_data.storage)

        res.content = self.get_res_content("cpu", fields.cpu)
        cpu_element: WebElement = self.driver.find_element("css selector", fields.cpu)
        cpu_element.send_keys(custom_data.cpu)

        res.content = self.get_res_content("ram", fields.ram)
        ram_element: WebElement = self.driver.find_element("css selector", fields.ram)
        ram_element.send_keys(custom_data.ram)

        res.content = self.get_res_content("software needed", fields.software_needed)
        software_element: WebElement = self.driver.find_element("css selector", fields.software_needed)
        software_element.send_keys(custom_data.software_needed)

        res.content = self.get_res_content("other specs", fields.other_specs)
        other_specs_element: WebElement = self.driver.find_element("css selector", fields.other_specs)
        other_specs_element.send_keys(custom_data.other_specs)

        return res

    @driver_wrapper 
    def start_return_fields(self, return_data: ReturnColumns, account_manager_email: str, res: Result = None) -> Result:
        '''Starts the return fields. This is only used if the `profile` field is
        `return`. It is going to be assumed that all items assigned to the user is returned.

        The address fields are handled within the method.

        Parameters
        ----------
            return_data: ReturnOrder
                The excel data for the return data.
            
            account_manager_email: str
                The account manager's email for the user.

            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("Return Fields")

        fields: ReturnFields = self.html_fields.return_fields
        self.logger.debug(f"Return data: {return_data}")

        res.content = self.get_res_content("request type", fields.request_type)
        self.utils.handle_dropdown(fields.request_type, key="return", send_enter=True)

        res.content = self.get_res_content("account manager", fields.account_manager)
        self.utils.handle_dropdown(fields.account_manager, key=account_manager_email, send_enter=True)

        # email fills the user, user already exists so no need to create.
        # however there is a chance no user will exist with the email, will have to skip.
        res.content = self.get_res_content("username", fields.user)
        user_element: WebElement = self.driver.find_element("css selector", fields.user)
        user_element.click()

        res.content = self.get_res_content("users dropdown list", fields.user_list)
        user_list_element: WebElement = self.driver.find_element("css selector", fields.user_list)

        # handles if the user does not exist.
        res.content = self.get_res_content("users dropdown list items", "(tag name) li")
        users_in_list: list[WebElement] = user_list_element.find_elements("tag name", "li")

        no_users_found: str = "no matches found"
        if len(users_in_list) == 0 or users_in_list[-1].text.lower() == no_users_found:
            self.logger.info(f"No users found with email {return_data["email"]}")

            # this is an error because the given email does not exist
            res.msg = "User does not exist within the system"
            res.err = True

            return res
        else:
            self.driver.send_keys(Keys.ESCAPE, pre_pause=0.3, pause=0.7)

        self.utils.handle_dropdown(user_element, key=return_data["email"], send_enter=True)

        # used to trigger the list of fields appearing and to handle populating the field
        res.content = self.get_res_content("equipment field", fields.equipment)
        equipment_element: WebElement = self.driver.find_element("css selector", fields.equipment)

        self.driver.click(equipment_element, pause=1)

        # this is not an actual dropdown like the others.
        res.content = self.get_res_content("equipment list dropdown", fields.equipment_list)
        equipment_dropdown_element: WebElement = self.driver.find_element("css selector", fields.equipment_list)

        res.content = self.get_res_content("equipment list dropdown items", "(tag name) li")
        equipment_list: list[WebElement] = equipment_dropdown_element.find_elements("tag name", "li")

        # assumes we are returning ALL devices.
        # NOTE: it is possible to support specific assets, but this requires to parse the
        # text for the asset tags and to pray the requestors gives the correct asset tag
        # in the excel file.
        # TL;DR: not worth it
        if len(equipment_list) > 0:
            res.content = self.get_res_content("equipment list form filling", "n/a")
            for _ in range(len(equipment_list)):
                self.driver.send_keys(Keys.ENTER, pause=.7, pre_pause=.5)
                equipment_element.click()

                # due to the dropdown being special, it does not trigger the dropdown menu again on click.
                # to bypass this entering a space will open the menu back up again.
                self.driver.send_keys(Keys.SPACE, pause=.7, pre_pause=.5)

            # required due to the element being on top once the loop ends 
            self.driver.send_keys(Keys.TAB, pause=.2)
            
            # TODO: key must be yes/no choice, also if yes then a new defective text field is enabled
            res.content = self.get_res_content("defective assets", fields.defective)
            self.utils.handle_dropdown(fields.defective, key="no", send_down=True, send_enter=True)

            # default to yes if it is invalid
            need_packaging: bool = "no" if return_data["packaging required"].lower() == "no" else "yes"
            send_down: bool = True if need_packaging == "no" else False
            res.content = self.get_res_content("packaging required", fields.packaging_required)
            self.utils.handle_dropdown(fields.packaging_required, key=need_packaging, send_enter=True, send_down=send_down)

            # NOTE: the address field starts here, however the fields are the same here as with other forms.
            add_res: Result = self.start_address_fields({
                "street": return_data["street"],
                "city": return_data["city"],
                "postal": return_data["postal"],
                "state": return_data["state"],
                "phone": return_data["phone"],
                "country": return_data["country"],
            })

            if add_res.err:
                res.msg = add_res.msg + " + Return Fields"
                res.content = add_res.content
                res.err = True
                return res

            res.content = self.get_res_content("ship date", fields.ship_date)
            ship_date: WebElement = self.driver.find_element("css selector", fields.ship_date)
            curr_date: str = datetime.now().strftime("%Y-%m-%d")
            ship_date.send_keys(curr_date)

            if return_data["additional notes"].strip() != "":
                res.content = self.get_res_content("additional details", fields.additional_details)
                additional_element: WebElement = self.driver.find_element("css selector", fields.additional_details)
                self.driver.send_keys(return_data["additional notes"], element=additional_element)
        else:
            self.logger.info(f"No equipment found for {return_data['full name']}")
        
        return res

    @driver_wrapper 
    def start_operating_system_fields(self, os_type: OperatingSystems, res: Result = None) -> None:
        '''Handles the operation system drop down menu.
        
        This is the 4th section of the normal ordering page.

        Parameters
        ----------
            os_type: OperatingSystems
                The OS type, it is a string that is type OperatingSystems.
            
            res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("Return Fields")

        fields: AddonFields = self.html_fields.addon_fields
        self.logger.debug(f"Operating system type: {os_type}")

        res.content = self.get_res_content("operating system fields", fields.operating_system)
        self.utils.handle_dropdown(value=fields.operating_system, key=os_type, send_tab=True, wait_time=.8)

        return res

    def check_cart(self) -> int:
        '''Checks the cart number and returns the amount in the cart.

        This reads from the cart which only works if the WebDriver is at the top of the page or
        can still read from the top of the page, before it can no longer be interacted with.
        
        If it fails to check the cart, it will return -1.
        '''
        try:
            cart_element: WebElement = self.driver.find_element("css selector", self.html_fields.checkout_fields.cart_dropdown)
        except Exception as e:
            self.logger.error(f"Failed to check cart: {e}")

            return -1

        # is expected to be "Cart {int}"
        cart_string: str = cart_element.text

        values: list[str] = cart_string.split()

        if len(values) > 1 and values[-1].isdigit():
            return int(values[-1])
        elif len(values) == 1:
            return 0

        return -1

    @driver_wrapper
    def company_fill_dates(self, data: CompanyData, fields: CompanyFields, res: Result = None) -> Result:
        '''Fills the dates of the company section.'''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("filling dates")
        
        dates: list[tuple[str, str]] = [
            (fields.desired_date, data["desired by"],),
            (fields.start_date, data["start date"],),
            (fields.end_date, data["end date"],),
        ]
        keys: list[str] = ["desired by", "start date", "end date"]

        for i, info in enumerate(dates):
            field: str = info[0]
            date_str: str = info[-1]
            key: str = keys[i]

            res.content = self.get_res_content(key, field)
            element: WebElement = self.driver.find_element("css selector", field)

            element.send_keys(date_str)
        
        return res

    @driver_wrapper
    def company_fill_company(self, data: CompanyData, fields: CompanyFields, res: Result = None) -> Result:
        '''Fills the customer ID, customer name, office ID, and office name of the company section.'''
        company_info: list[tuple[str, str]] = [
            (fields.customer_id, data["customer id"],),
            (fields.customer_name, data["customer name"],),
            (fields.office_id, data["office id"],),
            (fields.office_name, data["office name"],),
        ]
        keys: list[str] = ["customer id", "customer name", "office id", "office name"]
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("filling companies")

        for i, info in enumerate(company_info):
            field: str = info[0]
            company_str: str = info[-1]
            key: str = keys[i]

            res.content = self.get_res_content(key, field)
            element: WebElement = self.driver.find_element("css selector", field) 

            if element.get_attribute("value").strip() != "":
                self.driver.click(element, pause=.2)
                self.driver.action_driver\
                    .key_down(Keys.CONTROL)\
                        .key_down("A").pause(.1).send_keys(Keys.BACK_SPACE).pause(.1).key_up(Keys.CONTROL).perform()

            element.send_keys(company_str)
            
        return res

    @driver_wrapper
    def add_to_cart(self, pause: int | float = 1.5, res: Result = None) -> Result:
        '''Adds the order to the cart.
        
        This will always be accessible as the button to add to cart is fixed and sticky relative
        to the page position.
        
        Parameters
        ----------
        pause: int
            The pause time after clicking the button. It is recommended this to be
            1.5 seconds or longer due to the processing time after clicking
            the button. If it does not process then the order does not get added.
            By default this is 1.5 seconds.
        
        res: Result
                The Result of the method call. This should be left empty for the decorator
                to pass as an argument. By default it is None.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("Add to Cart")

        res.content = self.get_res_content("add to cart", self.html_fields.checkout_fields.add_to_cart_button)
        add_button: WebElement = self.driver.find_element(
            self.html_fields.checkout_fields.add_cart_selector,
            self.html_fields.checkout_fields.add_to_cart_button
        )
    
        self.driver.click(add_button, pause=pause)

        err_res: Result = self.check_error()
        if err_res.err:
            return err_res
        
        return res
    
    @driver_wrapper
    def upload_waiver(self, waiver_file: str, res: Result = None) -> Result:
        '''Uploads the waiver.'''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("Upload waiver")

        res.content = self.get_res_content("waiver upload", self.html_fields.company_fields.waiver)
        waiver_main_element: WebElement = self.driver.find_element("css selector", self.html_fields.company_fields.waiver)

        waiver_path: Path | None = u.get_file(Path("output"), waiver_file, skip_dir=True)
        if waiver_path is None:
            res.err = True
            res.content = self.get_res_content("waiver file search", "N/A")
            return res

        res.content = self.get_res_content("waiver input element", "N/A")
        waiver_input: WebElement = waiver_main_element.find_element("tag name", "input")
        waiver_input.send_keys(str(waiver_path.absolute()))

        return res
    
    @driver_wrapper
    def check_error(self, res: Result = None) -> Result:
        '''Checks for the error notification. This notification can occur after adding to cart.
        
        The error will be logged if one occurs.

        It will return a Resultt indicating if it failed or not.
        '''
        if res is None:
            res = Result()
        res.msg = self.get_res_msg("notifications (post add to cart)")
        res.content = self.get_res_content("notification", self.html_fields.checkout_fields.notification)

        # the notification is fixed on the screen
        notifcations_ele: WebElement = self.driver.find_element(
            "css selector", 
            self.html_fields.checkout_fields.notification,
        )
        noti_text: str = notifcations_ele.text
        noti_text_lower: str = noti_text.lower()

        # the notifications is also used for success, errors need to be checked
        err_texts: list[str] = ["error", "following fields are incomplete"]
        is_error: bool = False
        for err in err_texts:
            if err in noti_text_lower:
                is_error = True
        
        if is_error:
            self.logger.warning(f"Failed to add to cart: {noti_text}")

        res.err = is_error
        
        return res
    
    @driver_wrapper
    def wait_for_page_load(self, locator: Locator, element_value: str, new_timeout: int, _: Result = None) -> None:
        '''A blocking method used to wait for to confirm the page loads.
        It finds a target element value and waits until that target element is selectable,
        and then it will update the timeout to a lower time for the process.

        The caller is responsible for resetting the timeout back to its original timeout.
        '''
        # only care if it can be found, nothing is done on this element
        # the exception is caught by the wrapper
        self.driver.find_element(locator, element_value)

        self.driver.set_wait_timer(new_timeout)
    
    def get_res_msg(self, process: str) -> str:
        '''Creates a new string for Result.msg. `process` will be
        in title case by default.
        
        The output string is `Current process: {process}`.
        '''
        out: str = f"Current process: {process.title()}"

        return out
    
    def get_res_content(self, field: str, html_attribute: str) -> str:
        '''Creates a new string for `Result.content`.
        
        The given `field` will be in title case by default.

        The output will be `HTML Field: {field} | Value: {html_attribute}`.
        '''
        out: str = f"HTML Field: {field.title()} | Value: {html_attribute}"

        return out