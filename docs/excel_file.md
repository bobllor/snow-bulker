## About

An Excel file is used to automate the request orders for bulking. It holds the client and company information
needed to fill out the form.

The Excel file is 1:1 to how the form works, with the required form fields, required headers, and required
values being the same.
In case the form is changed, then these values, headers, and fields must be updated in the program as well.

The headers and values are *not case sensitive*.

> The Excel files may not have all fields on a single form. Other information on
> the form is obtained from the clients directly (ex: additional software) or 
> will always have a fixed value (ex: `Request Type`).

## Types

There are two types of profiles, which have an equivalent Excel file:
1. *Standard*: This is used for ordering new assets. These files are applicable to the profiles *`Dell i5/i7/i7 big` and `Custom`*.
2. *Return*: This is used for returning assets. These files are only applicable to the profiles *`Return`*.

The Excel files are expected to follow structured headers, which can be found in the `base-excel` folder. This is used for the
customer to fill out information for their end users to order.

If the values are not filled properly, then the program *will fail to parse the required data*.

## Gathering Excel Data

To ensure data integrity, the requestor should be informed of *general caveats* of the Excel files. 
- Column names should not be modified
- Additional columns included in the file *will be ignored*

There are other columns that require fixed values, which is given from the drop down list of the
ordering form. More details can be found below in the *attributes* section.

## Excel Column Attributes

The following sections are each of the required headers and their explanations.
The headers are in order of their respective file type.

### Standard Type

This is the Excel file that most orders will be using.

Potential columns for explanations:
- `Street`: This is street one and street two combined. *DO NOT INCLUDE* city, state, or postal 
in this field.
- `Operating Company`: The values are obtained from the form. The values *must* match.
- `Region`: The values are obtained from the form and it *must* be exactly as the form if used.

#### `Full Name`

The full name of the user. 

This is used for creating the user if they do not exist in the system as well.

#### `Email`

The email of the user.

Used to uniquely identify a user in the system to prevent duplicate accounts from being made.

#### `Employee ID`

The employee ID of the user. This will often be `TBD` but can be an actual employee ID number.

If the user already has an existing profile, then the given employee ID will overwrite the current
value.

#### `Operating Company`

The operating company of the user. This is used if the end user is part of an internal or external
company. If they are an *external company*, then the `Region` column is used. 

This is obtained from the field list when interacted with.
These values **must match**, otherwise there will be errors in the automation process.

#### `Division`

The division the client is part of. This is expected to be a number.

#### `Desired By`, `End Date`, `Start Date`

These date values are not required to be obtained from the requestor. Often times it is 
better to use *the current day* for `Desired By` and `Start Date`, and one year later
for `End Date`.
- `End Date` cannot exceed the day by one, this is due to the limitations placed by the 
ServiceNow developers.

For example, `11/25/2025 | 11/25/2025 | 11/25/2026`.

#### `Project ID`

The project ID for the client. This represents the project ID the client is tied to for their
work.

This *value may not exist* for the first time, in which case
the ServiceNow administrator role is needed to *create the project ID*.

Failure to create the Project ID will fail the form automation.

#### `Customer ID`

The customer ID the client is working for, i.e. the company ID.

#### `Customer Name`

The customer name the client is working for, i.e. the company name.

#### `Office ID`

The office ID of the client's work location.

#### `Office Name`

The city the client's office is located in or the name of the client's office.

#### `Street`

The address of the client to ship the device to. 

The value is *expected to be a combined street one and street two*.

#### `City`

The city of the address.

#### `State`

The state of the address. This can be the *full state name* or a *two-letter abbreviation*.

#### `Postal`

The ZIP code of the address.

#### `Phone`

The phone number of the consultant. 

If that is not available, the phone number of the requestor.

#### `Region`

The sales region that the request is going to for approvals. This routes the request to the correct
group of approvers that they handle.

This is only used *if the `Operating Company` is an external company*, otherwise it can be left empty.

The list of values can be obtained from the field list after interacting with the ordering form.

#### `Country`

Must be one of two values:
- United States
- Canada

No other countries are supported. Since we are US based, majority of the shipments goes to the United States.

### Return Type

This is the Excel file that only return orders are used for.

Potential columns for explanations:
- `Street`: This is street one and street two combined. *DO NOT INCLUDE* city, state, or postal 
in this field.
- `Packaging Required`: The values must be "Yes" or "No" only.

#### `Full Name`

The full name of the user. 

This is used for creating the user if they do not exist in the system as well.

#### `Email`

The email of the user.

Used to uniquely identify a user in the system to select them. This does not create
the user if they don't exist, unlike the Standard type.

#### `Street`

The address of the client to ship the device to. 

The value is *expected to be a combined street one and street two*.

#### `City`

The city of the address.

#### `State`

The state of the address. This can be the *full state name* or a *two-letter abbreviation*.

#### `Postal`

The ZIP code of the address.

#### `Phone`

The phone number of the consultant. 

If that is not available, the phone number of the requestor.

#### `Country`

Must be one of two values:
- United States
- Canada

No other countries are supported. Since we are US based, majority of the shipments goes to the United States.

#### Packaging Required

If the order requires packaging to be sent or if only the shipping label is needed.

This is a fixed value: `Yes` or `No`. If any other value is used in this column
then it will default to `Yes`.

#### Additional Notes

Additional notes for the order. 

This is *not required* to have a value.