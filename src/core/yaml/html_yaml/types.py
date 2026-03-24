from pydantic import BaseModel
from src.librelnium.support.types import Locator

# NOTE: every dropdown field has a related list field that comes up.
# there is a unique dropdown field in ReturnFields, this is the only dropdown handled
# differently.

class ClientFields(BaseModel):
    '''HTML fields of the client section.
    
    Dropdown fields:
        - `name`

    The `name` field dropdown reveals a new field that is used to gather
    information: `name_list`.

    If the `name` field has no found entries, then the the `not_found_button` is checked
    which enables three fields:
        1. `first_name`
        2. `last_name`
        3. `email`
    '''
    # email strings can be used on this field as well (and preferred)
    name: str
    # special list dropdown that only appears after interacting with name
    name_list: str
    first_name: str
    last_name: str
    email: str
    employee_id: str
    not_found_button: str

class CompanyFields(BaseModel):
    '''HTML fields of the company section.
    
    Dropdown fields:
        - `operating_company`
        - `project_id`
        - `account_manager`
        - `request_type`
        - `admin`
        - `usb`
    '''
    operating_company: str
    project_id: str
    region: str
    division: str
    sub_vendor: str
    account_manager: str
    customer_id: str
    customer_name: str
    office_id: str
    office_name: str
    request_type: str
    admin: str
    usb: str
    desired_date: str
    start_date: str
    end_date: str
    account_type: str
    regional_sub_account: str
    national_sub_account: str

class AddressFields(BaseModel):
    '''HTML fields for the address section.

    Dropdown fields:
        - `country`
        - `state` 
    '''
    street: str
    city: str
    country: str
    state: str
    postal: str
    phone: str

class CustomHardwareFields(BaseModel):
    '''HTML fields for the custom hardware section.'''
    make: str
    model: str
    storage: str
    ram: str
    cpu: str
    software_needed: str
    other_specs: str

class HardwareOptions(BaseModel):
    laptop_bag: str
    cable_lock: str
    docking_station: str
    surface_pro_dock: str
    wireless_combo: str
    lifechat: str
    monitor_20: str
    monitor_22: str
    monitor_24: str
    monitor_20_2nd: str
    monitor_22_2nd: str
    monitor_24_2nd: str
    apple_keyboard: str
    apple_mouse: str

class SoftwareOptions(BaseModel):
    '''The HTML fields for the software options. This must be updated with
    `SoftwareOptions` of the data YAML type.'''
    microsoft_office_web_apps: str
    microsoft_office_desktop_apps: str
    microsoft_exchange: str
    microsoft_project: str
    microsoft_visio: str
    symantec: str
    adobe_creative_cloud: str
    power_bi: str
    office_timeline: str
    adobe_photoshop: str
    adobe_illustrator: str
    adobe_indesign: str
    adobe_xd: str
    adobe_acrobat_pro: str
    adobe_acrobat_standard: str
    adobe_dreamweaver: str
    adobe_captivate: str

class AddonFields(BaseModel):
    '''HTML elements for addons section.
    
    Dropdown fields:
        - `operating_system`

    `software_not_listed` is a checkbox that enables a new field `desired_software`.

    `hardware` and `software` are options for additional hardware and software added
    onto the order.
    '''
    software_not_listed: str
    desired_software: str
    operating_system: str
    hardware: HardwareOptions
    software: SoftwareOptions

class ReturnFields(BaseModel):
    '''HTML fields for the return page.
    
    The `equipment` field is a dropdown but is not handled the same way as the other
    dropdowns. It still uses a new field list that appears after it is clicked on,
    `equipment_list`. 

    The `AddressFields` also exist on this page, but it is not included in this type.

    `defective` field reveals a new field if it has the value `yes`: `defective_text`.
     
    Dropdown fields:
        - `request_type`
        - `account_manager`
        - `user`
        - `defective`
        - `packaging required`
    '''
    request_type: str
    account_manager: str
    # supports email strings, preferrably also used over full name to eliminate duplicate cases
    user: str
    user_list: str
    equipment: str
    # the list of items when the equipment field is selected
    equipment_list: str
    defective: str
    # only appears if DEFECTIVE_FIELD has the value "yes"
    defective_text: str
    packaging_required: str
    ship_date: str 
    additional_details: str

class CheckoutFields(BaseModel):
    '''Fields handling the HTML elements related to checking out orders.'''
    cart_dropdown: str
    add_to_cart_button: str
    add_cart_selector: Locator = "name" # due to this being the only non-css selector, this will be selectable

class HTMLFields(BaseModel):
    '''HTML fields of all types of fields.
    
    This is configured by HTMLYamlLoader for the HTML YAML file.
    '''
    client_fields: ClientFields
    company_fields: CompanyFields
    address_fields: AddressFields
    custom_fields: CustomHardwareFields
    addon_fields: AddonFields
    return_fields: ReturnFields
    checkout_fields: CheckoutFields