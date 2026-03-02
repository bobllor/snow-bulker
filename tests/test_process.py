from src.core.process import ProcessFields
from src.core.yaml.data_yaml.types import CustomOrder
from src.support.types import Result, AddressData, ReturnColumns, CompanyData
from unittest.mock import patch, Mock
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException

INTERCEPT_EXC: ElementClickInterceptedException = ElementClickInterceptedException("Element intercepted")
TIMEOUT_EXC: TimeoutException = TimeoutException("Timeout for element search reached")
NO_ELE_EXEC: NoSuchElementException = NoSuchElementException("Unable to find element")

@patch("src.core.process.DriverUtils.handle_dropdown")
def test_address_fields(_, processor: ProcessFields):
    address_data: AddressData = {key: key for key in AddressData.__annotations__.keys()}

    res: Result = processor.start_address_fields(address_data)

    assert not res.err

@patch("src.core.process.DriverUtils.handle_dropdown")
def test_return_fields(_, processor: ProcessFields):
    return_columns: ReturnColumns = {key: key for key in ReturnColumns.__annotations__.keys()}

    mock_element: Mock = Mock()
    processor.driver.find_element.return_value = mock_element

    li_ele_one: Mock = Mock()
    li_ele_one.text = "Hello There"

    mock_element.find_elements.return_value = [li_ele_one]

    res: Result = processor.start_return_fields(return_columns, "email123@domain.com")

    assert not res.err

@patch("src.core.process.DriverUtils.handle_dropdown")
def test_company_fields(_, processor: ProcessFields):
    company_data: CompanyData = {key: key for key in CompanyData.__annotations__.keys()}

    res: Result = processor.start_company_fields(company_data, "email@domain.com")

    assert not res.err

@patch("src.core.process.DriverUtils.handle_dropdown")
def test_custom_fields(_, processor: ProcessFields):
    custom_order: CustomOrder = CustomOrder()

    res: Result = processor.start_custom_fields(custom_order)

    assert not res.err

@patch("src.core.process.ProcessFields.start_address_fields")
@patch("src.core.process.DriverUtils.handle_dropdown")
def test_fail_address_return_fields(mock_addr_func, _, processor: ProcessFields):
    return_data: ReturnColumns = {key: key for key in ReturnColumns.__annotations__.keys()}

    mock_element: Mock = Mock()
    mock_addr_func.return_value = Result(
        err=True, 
        msg="Current process: Address Fields", 
        content="HTML field: Field | Value: #some_address_value"
    )

    processor.driver.find_element.return_value = mock_element

    li_ele_one: Mock = Mock()
    li_ele_one.text = "Hello There"

    mock_element.find_elements.return_value = [li_ele_one]

    res: Result = processor.start_return_fields(return_data, "")

    assert res.err


@patch("src.core.process.ProcessFields.get_res_content", side_effect=INTERCEPT_EXC)
def test_click_intercept_address_fields(m1, processor: ProcessFields):
    address_data: AddressData = {key: key for key in AddressData.__annotations__.keys()}

    res: Result = processor.start_address_fields(address_data)

    assert res.err

@patch("src.core.process.ProcessFields.get_res_content", side_effect=INTERCEPT_EXC)
def test_exception_click_intercept_wrapper(p1, processor: ProcessFields):
    custom_order: CustomOrder = CustomOrder()

    res: Result = processor.start_custom_fields(custom_order)
    err_str: str = "intercept"

    assert res.err and err_str in res.msg

@patch("src.core.process.ProcessFields.get_res_content", side_effect=TIMEOUT_EXC)
def test_exception_timeout_wrapper(p1, processor: ProcessFields):
    custom_order: CustomOrder = CustomOrder()

    res: Result = processor.start_custom_fields(custom_order)
    err_str: str = "failed to find"

    assert res.err and err_str in res.msg

@patch("src.core.process.ProcessFields.get_res_content", side_effect=NO_ELE_EXEC)
def test_exception_no_such_wrapper(p1, processor: ProcessFields):
    custom_order: CustomOrder = CustomOrder()

    res: Result = processor.start_custom_fields(custom_order)
    err_str: str = "failed to find"

    assert res.err and err_str in res.msg

def test_software_options(processor: ProcessFields):
    res: Result = processor.start_software_option_fields(
        ["adobe acrobat pro", "adobe acrobat standard"]
    )

    assert not res.err

def test_hardware_options(processor: ProcessFields):
    res: Result = processor.start_hardware_option_fields(
        ["monitor 20", "monitor 22"]
    )

    assert not res.err

def test_invalid_software_options(processor: ProcessFields):
    res: Result = processor.start_software_option_fields(
        ["false value", "adobe acrobat standard"]
    )

    assert res.err

def test_invalid_hardware_options(processor: ProcessFields):
    res: Result = processor.start_hardware_option_fields(
        ["adobe acrobat pro", "monitor 22"]
    )

    assert res.err