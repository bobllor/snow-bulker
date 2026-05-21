## About

The data file holds the information of the Excel file and other order details. If this is not
configured correctly, then the file will not be parsed.
- The file must be named `data` and with any of the extensions: `yaml`, `yml`. 
- The file must be in the root of the project.
- It is not case sensitive.

There are *three required fields* that must exist in every section:
1. `profile`
2. `data_file`
3. `account_manager_email`

All YAML fields and values are **case insensitive**.

```yaml
# example
normal dell i7s company 2:
  profile: Dell i7 Big
  account_manager_email: manager.email@domain.com
  data_file: company2-data.xlsx
  desired_software: Adobe AfterEffects
  software:
    - adobe dreamweaver
    - adobe creative cloud
    - microsoft office web apps
  hardware:
    - "22 monitor"
    - wireless combo 
custom dell i5s company 2:
  profile: Custom
  account_manager_email: manager.email1@domain.com
  data_file: company2-data.xlsx
  email_cache: company2-custom-dell-i5s-cache.txt
  waiver_file: "Waiver.docx"
  account_type: Regional
  custom_order:
    model: latitude 5450
    make: Dell
    ram: 16
    storage: 512 gb ssd
    cpu: intel i7
```

## Sections

The YAML configuration are divided into *sections*, which represents a separate entry for a bulk order.
This uses a *dictionary* structure.

If multiple sections are defined, the program will run through each section once. If a section needs to be
skipped or doesn't want to be processed, adding the key-value `ignore: true` under the target section will
prevent it from being ran.

The following example demonstrates three sections for bulking.

```yaml
company 1:
  # ...
company 2:
  # ...
  ignore: true # skips this section
company 3:
  # ...
```

## Custom Orders

If the `profile` field is `custom`, this will require a `custom_order` dictionary to be added into the YAML.
It signals an order for an asset that is not in-stock, and requires specifications to be listed from the client.

This is part of the *standard* profile.

## Attributes

The following attributes are used in the YAML file. Any attributes labeled with `Required` must have a value
in a section.

### `account_manager_email` (Required)

The email of the manager for the client.

Since the request is coming from your account, this would be the *requestor's email*.
Getting the correct account manager email can be done as well.

```yaml
account_manager_email: john.doe@example.gov
```

### `account_type`

The type of account for the company of the user.

This is either `regional` or `national`. It is only used if the operating company contains `staffing`, otherwise
it will do nothing for other operating company types.

By default it is `regional`.

### `custom_order`

Key-value attributes for the specs of the custom order, only for hardware orders. 
This only applies **if the `profile` field has the property `custom`**, otherwise it will be ignored.

It has seven attributes:
  - `model`: Required, the device model name.
  - `make`: Required, the manufacturer of the device.
  - `cpu`: Required, the processor of the device.
  - `ram`: Required, how much RAM the device needs.
  - `storage`: Required, how much storage is needed, and if it is an HDD, SSD, NVME, etc...
  - `other_specs`: Optional, indicates other specs of the hardware. Can also be used for notes.
  - `software_needed`: Optional, indicates what software is needed on the device.

If any required values are missing or does not have a value, then the program will not run and an error will occur.
Not all custom orders uses all required attributes, in which case `N/A` can be written as a filler, but
any value can be added as long as it is not empty.

```yaml
custom_order:
  model: "Chromebook Plus Spin 714 CPE794-1N - AI READY - 14 inch"
  make: "Acer"
  cpu: "155u intel core ultra 7"
  ram: 16
  storage: "256 SSD"
```

### `data_file` (Required)

The name of the Excel file. By default, the program searches the files in the `data` folder of the
`output` in the project root. An absolute path can be used, which will ignore the `data` folder. If this does not
exist, then it will search the file name in the `data` folder.

Sub-folders do not effect the file searching process, the program will recursively search `data` 
for the exact file, otherwise the program will fail to run.

The file name *must end* in `.xlsx`.

```yaml
company 1:
  data_file: "an excel file.xlsx"
company 2:
  data_file: "C:\\Users\\defaultuser0\\downloads\\company-2-data.xlsx"
```

### `desired_software`

A string literal that is used to add software to the request that doesn't exist in the option menu.

It takes the whole string literal entered in the field.

```yaml
desired_software: "Adobe AfterEffects, Global Protect VPN, Avast Business"
```

### `email_cache`

The email cache file name, used to cache user emails when an order is successfully added to the cart. 
It prevents duplicate users from being entered more than once in case the source data is incorrectly inputted.

If no value is given, then it will default to the cache file name `default_cache.txt`.

If the value `ignore` is used as the value, it will *not attempt to write to the cache* and will always
process an order without checking if the user has already been processed.

```yaml
email_cache: "company-1-cache.txt"

# will not write to cache
email_cache: ignore
```

### `hardware`

A sequence of string literals for additional hardware. This is used if each order includes extra peripherals with
the laptop.

It will check the boxes on the form for the program.

Invalid entries will be ignored.

Values:
  - `laptop bag`
  - `cable lock`
  - `surface pro dock`
  - `docking station`
  - `wireless combo`
  - `lifechat`
  - `20 monitor`
  - `22 monitor`
  - `24 monitor`
  - `2nd 20 monitor`
  - `2nd 22 monitor`
  - `2nd 24 monitor`
  - `apple keyboard`
  - `apple mouse`

The following example includes a laptop bag, a 20" monitor, and a wireless combo included with every order.

```yaml
hardware
  - "laptop bag"
  - "20 monitor"
  - "wireless combo"
```

### `ignore`

A boolean literal used to skip a section if `true`. 

By default it is `false`, the section will always be attempted to run every time.

```yaml
ignore: true
```

### `os_type`

Indicates what operating system the request wants. By default it will be Windows 11.

It is best to leave this alone, as all the laptops outside of a few companies. All devices
should be compliant and use Windows 11.

Values:
  - `windows 11`
  - `windows 10`
  - `no operating system`

### `profile` (Required)

The profile that the order is being used for. This represents the different types of orders
through ServiceNow.

Values: 
  - `Dell i5`
  - `Dell i7`
  - `Dell i7 Big`
  - `Custom`
  - `Return`
  - `Exchange`

The option `Custom` will require to have the field [custom_order](#custom_order) with required attributes filled out.
The program will fail to run if this requirement is not met.
- It will still use the standard Excel format.

The option `Return` will tell the program to parse the given Excel file *as a Return Excel file*. This must follow
its specific formatting which are different from the standard Excel file. To read more, [click here](./excel_file.md).

The option `Exchange` will trigger a new workflow with handling requests that only are used for software. This is
one of many that will potentially be added.

### `software`

A sequence of string literals for additional software. This is used if the orders require listed software in the ordering form.

If the software is not listed in the values below but is needed, it should be included with the `Desired Software` attribute.

It will check the boxes on the form for the program. Otherwise, invalid entries will be ignored.

Values:
  - `microsoft office web apps`
  - `microsoft office desktop apps`
  - `microsoft exchange`
  - `microsoft project`
  - `microsoft visio`
  - `symantec`
  - `adobe creative cloud`
  - `power bi`
  - `office timeline`
  - `adobe photoshop` 
  - `adobe illustrator`
  - `adobe indesign`
  - `adobe xd`
  - `adobe acrobat pro`
  - `adobe acrobat standard`
  - `adobe dreamweaver`
  - `adobe captivate`

### `waiver_file`

The waiver file name located in the `output` folder. This is used to upload a waiver file from the
local disk into the *input element* of the form.
If given, it will trigger a new workflow to add the file to the form.

By default this is an empty string and is *not required*. However, if used, it must exist otherwise
the order will fail.