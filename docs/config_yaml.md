## About

The `config` file is used to modify the program and hold the initialization data for setting up the
WebDriver to start automation.

The file holds the information needed to get through the *authentication/login process* and holds the URLs
for *each profile*.

This file is **required**. The file will be read twice, once when the program is started for the first time
and another time continuously when the automation process starts. 
- The latter hot loads the config file.

*Every non-HTML attribute* are expected to be in lowercase, while HTML attributes *are case sensitive*
and the value defined in the file must be the same as it is found on the page.

```yaml
# sample file
auth_info:
  main_url: "service-now.com/site"
  main_html_attribute: an-random-attribute-on-the-page-after-auth
  main_html_selector: id
  url_substring: service-now # used to check the url if authentication was successful
  login_info:
    multi_page: true
    stay_signed_in_locator: css selector
    stay_signed_in_element: ".classes.are.here"
    login_locators:
      - name
      - name
      - css selector
    login_elements:
      user_element: login-name
      password_element: passwd-name
      button_element: "#signin-selector" # must be in quotations due to this being an ID selector
settings:
  headless: false
  stream_log_level: "info"
  data_folder: "/path/to/data/folder"
  cart_delay_time: 5
  timeout: 30
profile_url: 
  returns: "profile-url.com" 
  custom: "profile-url.com" 
  dell_i5: "profile-url.com" 
  dell_i7: "profile-url.com" 
  dell_i7_big: "profile-url.com"
```

## Errors

Errors are handled depending on when the configuration is called. A field is considered an error *if the field's value
is an empty string*.
- Invalid entries will be replaced with a default value.
- Most default values are an empty string, but some fields have a proper default value.
- The default values will be shown below in the attributes section.

On program start, if there are errors with the validation, then *default values replaces the incorrect values*. This is only
done to prevent the program from crashing on load.

When the automation process starts, the file is read again. If an error occurs here, *the process will not continue* and an error
message will be displayed. It will then be sent back to the main menu.
The error message contains the *field names that are empty strings*. These names must be corrected in order to start the process. 

## Mappings

There are three dictionaries used in the file:
1. `settings`: Contains the meta information for the program.
2. `auth_info`: Contains the authentication information to access the website for automation.
3. `profile_url`: Contains the URLs for the profiles for the standard and return Excel types.

### Settings Information

This dictionary holds the information for the program logic. These values are not required
and will not cause an error if left empty.

#### `headless`

Default: `false`

Makes the WebDriver headless, in other words the browser is ran in the background when the automation process starts.

> IMPORTANT
>
> If this is `true`, then do not interrupt the program with `Ctrl + C` during the automation process.
> The program will likely fail to close the browser and be left open, consuming resources despite being unused. 
> It is *recommended to leave this as `false`* since it can manually be closed in case of failure.

#### `stream_log_level`

Default: `info`

The level for the log which will *display on the terminal*. By default, it is `info`.
This does not effect the logging to file output.

This field has *fixed values*:
- `debug`
- `info`
- `error`
- `warning`
- `critical`

#### `timeout`

Default: `30`

Timeout is the length of time for a page load before a timeout exception occurs. This is
only used during the initial load of each form submission, before it changes back to
a 7 second timer for each field.

#### `cart_delay_time`

Default: `3`

The wait time after adding the order to the cart. It is recommended this be kept at a lower time
in order to read the notifications, as that occurs afterwards and disappears in a short amount
of time.

The longer


### Authentication Information

This dictionary holds the information for authenticating into SeviceNow to access the ordering form.
This is required, and all fields *must have a value* and not be an empty string.
- The only exception to this is the `main_html_selector` field.

#### `main_url`

Default: `""`

The URL to the ServiceNow instance. This can be any URL of a ServiceNow instance. It is used to
trigger the authentication process and validate that the process suceeded.

This is intended to be used with the `main_html_attribute` for validation after auth.

#### `main_html_attribute`

Default: `""`

This is any element's attribute on the `main_url`. It can be any attribute, but it must be the 
searchable based on the selector given with `main_html_selector`.

```yaml
main_html_attribute: "#an-id-attribute" # main selector is css selector, note the selector for the attribute.
main_html_selector: css selector

main_html_attribute: an-id-attribute # no selector required as the main selector searches by ID
main_html_selector: id
```

#### `main_html_selector`

Default: `id`

The selector used to search for the `main_html_attribute` for auth validation. By default this is
selects by `id`.

This field has *fixed values*:
- `id`
- `xpath`
- `link text`
- `partial link text`
- `name`
- `tag name`
- `class name`
- `css selector`

#### `url_substring`

Default: `""`

Any string that is found in the URL. This is used to determine if authentication is required.

Often times it will be required unless the WebDriver uses the default profile from Chrome. Regardless,
it is recommended to put a substring value in the event authentication is required.

#### `login_info`

Default: `dictionary`

This is a dictionary that holds its own values.

The related fields will have the title formatted as `login_info: ...`

#### `login_info`: `multi_page`

Default: `true`

A flag used to indicate if after a successful authentication, a new page or popup appears that
asks if you "want to stay logged in".

By default this is `true` as the authentication is expected to be *through Microsoft*, which has
this prompt.

#### `login_info`: `login_locators`

Default: `[]`

A collection of selectors. This is the same selectors as `main_html_selector`, but instead in an array format.

This represents the selectors used for each value of `login_elements`, starting in order from `user_element`,
`password_element`, and `button_element`.

This collection is expected to be a fixed length of *three entries*. 
- `<3`: The program will assume all missing entries to be the selector `css selector`.
- `>3`: The program only selects the first three entries. All other entries past the first three *are ignored*.

By default it is an empty list and will default to *three `css selector` entries*.

This field has *fixed values*:
- `id`
- `xpath`
- `link text`
- `partial link text`
- `name`
- `tag name`
- `class name`
- `css selector`

```yaml
# example
login_locators:
    - name # selects the username element by its name attribute
    - name # selects the password element byh its name attribute
    - css selector # selects the sign in button by its selector
login_elements:
    user_element: login-name
    password_element: passwd-name
    button_element: "#signin-selector" # ID selector since it uses a css selector
```

#### `login_info`: `login_elements`

Default: `dictionary of empty values`

This is a dictionary that holds the element attributes for the username, password, and sign in button.

It contains three fields:
1. `user_element`: Represents the *username* input field.
2. `password_element`: Represents the *password* input field.
3. `button_element`: Represents the *sign in* button.

By default, all of these values is an empty string. These are *required*.

#### `login_info`: `stay_signed_in_locator`

Default: `id`

The locator of the "Stay signed in" button element.

This field has *fixed values*:
- `id`
- `xpath`
- `link text`
- `partial link text`
- `name`
- `tag name`
- `class name`
- `css selector`

#### `login_info`: `stay_signed_in_element`

Default: `""`

The HTML attribute of the "Stay signed in" button element.

Due to the authentication being a Microsoft login, this is expected to appear.

### `profile_url`

This is a dictionary that holds the URLs for each profile. During the program run,
it will access the URL given to these values below:
- `returns`
- `custom`
- `dell_i5`
- `dell_i7`
- `dell_i7_big`

All values will default to an empty string, these are *required*.