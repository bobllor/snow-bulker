## About

An automation tool for bulking ServiceNow asset orders and asset returns for end users, using
Selenium and pandas to power the workflow.

## Requirements

- Python >= 3.12.4
    - Any other versions below 3.12.4 are not guaranteed to work.
- Git
- ChromeDriver / Chrome
- Windows 10 22H2 or later

> <p style="color:red">IMPORTANT</p>
>
> SnowBulker is built for and used for a specific company's ServiceNow instance. 
> All other ServiceNow instances are not supported, but if 
> the infrastructure is similar it can be used.

## Getting Started

It is expected to use *Git Bash* and the documentation will be using Bash syntax.
In the folder `scripts/ps-helpers` contains PowerShell files equivalent to the helper Shell scripts
that are named.

```shell
# clone and enter the repository
git clone https://github.com/bobllor/snow-bulker
cd snow-bulker

# run the build script to initialize the project
bash build.sh
```

The script `build.sh` is used to initialize the project:
- It creates the folders used by the program in `output`, including the `data` folder for the Excel files.
- It sets up the Python virtual environment.
- It creates a `configs` folder for holding different environment YAML files.

## Usage

By default the WebDriver uses the ChromeDriver, other WebDrivers are not supported.

The program uses YAML files to run the program and to load the client data to automate the forms. 
The files are *case insensitive* and must end with `.yml` or `.yaml`.

The YAML files are complex due to the use of HTML attributes and amount of fields. It is recommended to work with the
*sample files* in `samples` for a starting point.

There are three YAML files that must exist in the *project's root folder* before the automation can run:
1. `data`: Contains the information about the client and required data files. 
For more information, [click here](docs/data_yaml.md). 
2. `html`: Contains the HTML elements of the form for automation.
For more information, [click here](docs/html_yaml.md).
3. `config`: Used to configure the program and the data for the login process.
For more information, [click here](docs/config_yaml.md).

These files *must begin with* `data`, `html`, and `config` followed by a YAML extension. This is required for the program
to read the files and for the support script `switch-env.sh` to be used.

Finally, run `py main.py` to start the automation process.

### Environment Switching

It is recommended to have multiple YAML files for different environments, for example having a `prod` and `testing`
environments. The support script `switch-env.sh` is used to assist with this context switching,
which takes an argument *folder* to create a hardlink of the files in the current folder. 
- The files can be named anything, but **it must begin with the required names above**, otherwise the script will
not recognize the file. See the example below.
- Any changes to the new file *will also reflect to the original file*. Deleting either file will not do anything
due to it being a hardlink.

> `data.qa.example.yml` (✔): starts with `data` and ends with `.yml`
>
> `config.qa.EXAMPLE.YAML` (✔): starts with `config` and ends with `.YAML`
>
> `qa.data.example.yml` (✖): does not start with `data`

When the `build` script is run, a `configs` folder is created. This is where the YAML files can be stored, but
any preferred folder can also work.

An example `configs` folder with different environments:

```
configs/
  default/
    config.prod.yml
    html.prod.yml
  company-one-prod/
    data.company-one.yml
  company-two-prod/
    data.company-two.yml
  return-company/
    data.return.yml 
  testing/
    config.qa.yml
    html.qa.yml
    data.qa.yml
```

The folder can be specified as an argument and it will create the hard links into the current directory:
```shell
# creates a hard link of all files in testing into the current directory
./switch-env.sh configs/testing
```

> <p style="color:red">! IMPORTANT FOR WINDOWS ONLY !</p>
> 
> The command `ln` with Git Bash may have an issue with creating the hardlinks due to a `Permission denied` error.
> Git Bash must be ran as administrator or the current session must have Administrator rights. In this case,
> using the PowerShell script `switch-env.ps1` resolves the YAML environment switching.

### Excel Files

Excel files are the required files that starts the automation of the ServiceNow fields. 
They contain the client information needed to successfully fill an order form to order an asset from ServiceNow.

Excel files are expected to be in `./output/data/`. The program searches and reads Excel files from the `data` folder, which 
is based on the entry given in `data_file` of the `data` YAML.

```yaml
# data.yml
section:
  # other entries...
  data_file: excel-to-parse-name.xlsx # the file name that is being looked for
```

There are two types of files related to each profile: standard and return.
1. *Standard*: This is the normal Excel file used for ordering new assets.
2. *Return*: This is a special Excel file used for returning existing assets.

### Authentication / Login

When the program is launched, logging into ServiceNow is expected to be with a **Microsoft company portal login page**.
A ServiceNow account with sufficient access and roles is needed in order to access the site and the form.
- If the login is not with Microsoft, there is customization allowed for this with the `config` YAML file.

When the WebDriver launches for the first time and if no username or password is given, then it will prompt an input for both. 
By default, the *password input is hidden*.
There will be three attempts at the login before it fails. The failures are determined by a WebDriver exception or checking
the URL after every login attempt.

A substring is used to check the URL after a login attempt, which by default is `service-now`. 
It matches this substring to the URL to confirm if the login was successful.
- This value can be changed in the `config` file with the key `url_substring` for the dictionary `auth_info`.

```yaml
# config.yml
auth_info:
  url_substring: service-now
```

The login can be skipped if the WebDriver uses the default signed-in Chrome profile. However, this is often only available to 
work laptops, so it is expected to login every time. 
Alternatively, an `.env` file with the credentials can be used to automate the login process. The two keys used are
`SN_USERNAME` and `SN_PASSWORD`.

```env
SN_USERNAME=user1234
SN_PASSWORD=AnExamplePassword
```

### Logging

All logging output goes into the `./output/logs` folder by default.

Settings related to the logging can be found in the `config` YAML file under the `Settings` dictionary.

By default the program logs to the console at the *info* level or above. This level can be modified with the
key `log_level`.

In case of Selenium based errors, screenshots for an error can be enabled. This is the key `enable_log_screenshot` 
in the `config` YAML file.

## Development

The program *uses Selenium* as its core, knowing how to interact with HTML elements and Selenium knowledge is required.
The program uses my custom Selenium wrapper `Librelnium` to assist with the Selenium based tasks.

> <p style="color:red">! IMPORTANT !</p>
>
> `Librelnium` is still work in progress as it was made early in my programming journey.
> It is important to know that the library is not available with `pip` and is included in this repository. 
> Getting an updated version or updating the library here will need to be updated in the
> [original repository as well](https://github.com/bobllor/librelnium).