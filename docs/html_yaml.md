## About

The HTML file holds the element attributes of the HTML on the form. Since most profiles
will use the same form outside of the `Return` profile, they share the same HTML
fields.

This HTML file is primarily used to ensure that the fields can easily be updated, whether
it be through an attribute change, deletion of a field, or addition of a field.

There are seven dictionaries inside the file, each representing a section of the form:
1. `client_fields`: Consists of the user fields.
2. `company_fields`: Consists of the company information fields.
3. `address_fields`: Consists of the user's address fields.
4. `custom_fields`: Consists of the custom hardware fields, this is only applicable to the `Custom` profile.
5. `addon_fields`: Consists of the optional assets fields.
6. `return_fields`: Consists the fields used on the `Return` profile.
7. `checkout_fields`: Conists of the fields related to ordering the assets.

> IMPORTANT
>
> The attributes are all *expected to be of type `css selector`*. Only the checkout field
> uses a selector.
>
> The attributes *are case sensitive*. The value `#an-id-here` is not the same as the value
> `#An-ID-Here`, and will cause the program to fail in locating the element on the page.

## Example

```yaml
client_fields:
  name: "#field_a1"
  name_list: "#dropdown_a1" # the element containing the list of names after clicking on the name field
  first_name: "#field_a2"
  last_name: "#field_a3"
  email: "#field_a4"
  employee_id: "#field_a5"
  not_found_button: "#button_a1"
company_fields:
  operating_company: "#field_b1"
  project_id: "#field_b2"
  region: "#field_b3"
  division: "#field_b4"
  sub_vendor: "#field_b5"
  account_manager: "#field_b6"
  customer_id: "#field_b7"
  customer_name: "#field_b8"
  office_id: "#field_b9"
  office_name: "#field_b10"
  request_type: "#field_b11"
  admin: "#field_b12"
  usb: "#field_b13"
  desired_date: "#field_b14"
  start_date: "#field_b15"
  end_date: "#field_b16"
address_fields:
  street: "#field_c1"
  city: "#field_c2"
  country: "#field_c3"
  state: "#field_c4"
  postal: "#field_c5"
  phone: "#field_c6"
custom_fields:
  make: "#field_d1"
  model: "#field_d2"
  storage: "#field_d3"
  ram: "#field_d4"
  cpu: "#field_d5"
  software_needed: "#field_d6"
  other_specs: "#field_d7"
addon_fields:
  software_not_listed: "#field_e1"
  desired_software: "#field_e2"
  operating_system: "#field_e3" # dropdown menu
  hardware: # all of these values are checkboxes
    laptop_bag: "#field_e4"
    cable_lock: "#field_e5"
    docking_station: "#field_e6"
    surface_pro_dock: "#field_e7"
    wireless_combo: "#field_e8"
    lifechat: "#field_e9"
    monitor_20: "#field_e10"
    monitor_22: "#field_e11"
    monitor_24: "#field_e12"
    monitor_20_2nd: "#field_e13"
    monitor_22_2nd: "#field_e14"
    monitor_24_2nd: "#field_e15"
    apple_keyboard: "#field_e16"
    apple_mouse: "#field_e17"
  software: # all of these values are checkboxes
    microsoft_office_web_apps: "#field_f1"
    microsoft_office_desktop_apps: "#field_f2"
    microsoft_exchange: "#field_f3"
    microsoft_project: "#field_f4"
    microsoft_visio: "#field_f5"
    symantec: "#field_f6"
    adobe_creative_cloud: "#field_f7"
    power_bi: "#field_f8"
    office_timeline: "#field_f9"
    adobe_photoshop: "#field_f10"
    adobe_illustrator: "#field_f11"
    adobe_indesign: "#field_f12"
    adobe_xd: "#field_f13"
    adobe_acrobat_pro: "#field_f14"
    adobe_acrobat_standard: "#field_f15"
    adobe_dreamweaver: "#field_f16"
    adobe_captivate: "#field_f17"
return_fields:
  request_type: "#field_g1"
  account_manager: "#field_g2"
  user: "#field_g3"
  user_list: "#dropdown_g1" # list of names after clicking on the user field
  equipment: "#field_g4"
  equipment_list: "#dropdown_g2"
  defective: "#field_g5"
  defective_text: "#field_g6"
  packaging_required: "#field_g7"
  ship_date: "#field_g8"
  additional_details: "#field_g9"
checkout_fields:
  cart_dropdown: "#field_h1"
  add_to_cart_button: action_h1
  add_cart_selector: name
```

## Fields

Due to the amount of entries in the file, the keys of each field dictionary will not be explained.
Each section will explain what the field is used for and the behavior of the fields.

The example above can be used. Comments will also exist on certain fields where it requires special
care, this will also be explained in their respective sections.

### `client_fields`