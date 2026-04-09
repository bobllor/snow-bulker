from pathlib import Path
from src.core.yaml.data_yaml.types import Profile
from src.core.yaml.config_yaml.config_yaml_loader import ConfigYamlLoader
from src.core.yaml.config_yaml.types import ProfileUrl, Config
from src.support.types import Result
from typing import Iterable, Any

def get_config(root: Path, file: Path | str, yaml_extensions: list[str], config_loader: ConfigYamlLoader) -> Config:
    '''Reads the config YAML and returns a Config. If the file does not exist,
    then return a default Config.
    
    This is only used for initialization, the loop will hotload the config file.
    '''
    config: Config = Config()

    # the loop will hot load the config file again, this is to setup the initial state
    cfg_file: Path | None = get_file(root, file, exts=yaml_extensions, skip_dir=True)
    if cfg_file is not None and cfg_file.exists():
        raw: dict[str, Any] = config_loader.read(cfg_file)
        cfg_res: Result[Config] = config_loader.validate(raw)

        # config has defaults, if this errors out then do nothing
        # starting the program will hotload the file anyway.
        if not cfg_res.err:
            config = cfg_res.content
    
    return config

def format_pid(pid: str) -> str:
    '''Formats the PID for missing leading zeroes. If the PID contains alphabets,
    then it will do nothing and return the PID unaffected.
    '''
    if not pid.isnumeric():
        return pid

    LEAD_ZEROES_COUNT: int = 4
    zeroes_found: int = 0

    for i in range(4):
        if pid[i] == "0":
            zeroes_found += 1
    
    if zeroes_found == 4:
        return pid

    zeroes_list: list[str] = ["0" for _ in range(LEAD_ZEROES_COUNT - zeroes_found)]

    return f"{"".join(zeroes_list)}{pid}"

def get_us_state(state_full_or_abbrev: str) -> str:
    '''Gets the full US state name. It handles abbreviations and the full state name.
    
    If not found, then it will return an empty string.
    '''
    state_full_or_abbrev = state_full_or_abbrev.strip()
    us_state_to_abbrev = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "District Of Columbia": "DC",
        "American Samoa": "AS",
        "Guam": "GU",
        "Northern Mariana Islands": "MP",
        "Puerto Rico": "PR",
        "United States Minor Outlying Islands": "UM",
        "Virgin Islands US": "VI",
    }

    if len(state_full_or_abbrev) == 2:
        state_full_or_abbrev = state_full_or_abbrev.upper() 
    else:
        state_full_or_abbrev = state_full_or_abbrev.title() 

    # handles abbreviations
    inverted_map: dict[str, str] = {value: key for key, value in us_state_to_abbrev.items()}

    state: str = inverted_map.get(state_full_or_abbrev, "")

    if state_full_or_abbrev in us_state_to_abbrev:
        state = state_full_or_abbrev

    return state

def get_canada_province(state_full_or_abbrev: str) -> str:
    '''Gets the Canada province, it handles the abbreviation and full province name.
    
    If not found, then it will return an empty string.
    '''
    state_full_or_abbrev = state_full_or_abbrev.strip()
    can_province_abbrev: dict[str, str] = {
        'Alberta': 'AB',
        'British Columbia': 'BC',
        'Manitoba': 'MB',
        'New Brunswick': 'NB',
        'Newfoundland And Labrador': 'NL',
        'Northwest Territories': 'NT',
        'Nova Scotia': 'NS',
        'Nunavut': 'NU',
        'Ontario': 'ON',
        'Prince Edward Island': 'PE',
        'Quebec': 'QC',
        'Saskatchewan': 'SK',
        'Yukon': 'YT'
    }

    if len(state_full_or_abbrev) == 2:
        state_full_or_abbrev = state_full_or_abbrev.upper() 
    else:
        state_full_or_abbrev = state_full_or_abbrev.title() 

    inverted_can_map: dict[str, str] = {value: key for key, value in can_province_abbrev.items()}
    state: str = inverted_can_map.get(state_full_or_abbrev, "")

    if not state and state_full_or_abbrev in can_province_abbrev:
        state = state_full_or_abbrev

    return state

def get_excel(file_name: str, folder: Path) -> Path | None:
    '''Retrieves the Path of the given Excel file from the given folder Path. 
    
    If the file does not exist, then None will be returned.
    '''
    file: Path | None = None
    file_name = file_name.lower()

    for child in folder.iterdir():
        child_name: str = child.name.lower()

        if child.is_dir():
            file = get_excel(file_name, child)

            if file is not None:
                return file

        if file_name == child_name:
            return child
        
    return file

def get_profile_url(profile: Profile, profile_urls: ProfileUrl) -> str:
    '''Gets the profile URL from the given ProfileUrl.
    
    Parameters
    ----------
        data: dict[str, Config]
            The config data.

        profile_urls: str
            The ProfileUrl object containing the URLs.
    '''
    urls: dict[Profile, str] = {
        "dell i5": profile_urls.dell_i5,
        "dell i7": profile_urls.dell_i7,
        "dell i7 big": profile_urls.dell_i7_big,
        "custom": profile_urls.custom,
        "return": profile_urls.returns,
    }
    profile = profile.lower()

    return urls[profile]

def get_file(root: Path, file: Path | str, *, exts: Iterable[str] = [], skip_dir: bool = False) -> Path | None:
    '''Searches for a file in a given root path and return that Path. By default it searches
    the root path recursively. If the path is not found, then it will return None.

    The file must either have an extension or the optional `exts` is given if the file does not come 
    with an extension. If neither are true then the function will return None.

    Parameters
    ----------
        root: Path
            The root path directory to search in.
        
        file: Path | str
            The file path or file name. The function will convert this to a string and search
            an exact match. If it is ambigious, then it will return the first match.
        
        exts: Iterable[str]
            Any iterable of strings that represents the extension of the file. If given, the extensions
            will append itself to the given file and will be searched for.
        
        skip_dir: bool
            If True, then do not recursively search through folders in the root path. By default
            this is False.
    ''' 
    # normalization
    file = Path(file)
    suffix: str = file.suffix

    # if no suffix is given and no extensions are given, then do not continue
    if suffix == "" and len(exts) == 0:
        return None

    iter_files: list[Path] = []

    if len(exts) > 0:
        name_only: str = file.name.replace(suffix, "")

        # removing all periods for normalization
        exts = [ext.replace(".", "") for ext in exts]

        iter_files.extend([name_only + f".{ext}" for ext in exts])
    else:
        iter_files.append(file)

    # iterating each file and comparing it to each child file
    # iterations are done if optional exts are given
    for iter_file in iter_files: 
        for child in root.iterdir():
            if child.is_dir() and not skip_dir:
                found: Path | None = get_file(child, file, exts=exts)

                if found is not None:
                    return found

            path: str = str(child).lower()
            given_file: str = str(iter_file).lower()

            if given_file == path or given_file in path:
                # ensures only files are selected.
                if not child.is_dir():
                    return child

    return None

def get_path_files(root: Path) -> list[Path]:
    '''Recursively traverses a given root path and return a list consisting of the
    full path of all files found. Any directories are not included in the list.
    
    Parameters
    ----------
        root: Path
            The path that is being searched in. This must be a directory.
    '''
    data: list[Path] = []

    for file in root.iterdir():
        if file.is_dir():
            child_data: list[Path] = get_path_files(file)

            data.extend(child_data)
        else:
            data.append(file)
    
    return data

def format_validate_postal(postal: str) -> str:
    '''Formats and validates the postal. This works for both US and Canada postals.

    If the postal is less than 5 in length, then it will automatically append leading 0s.
    This is due to Excel and Pandas trimming leading 0s with numbers.

    If the length of the postal is greater than 5 and is not a Canada postal, then
    a ValueError is raised.
    '''
    is_canada: bool = is_canada_postal(postal)
    if is_canada:
        return postal

    if len(postal) > 5:
        raise ValueError(f"Invalid postal {postal} given")

    # always going to assume missing numbers is a leading 0, this is due to excel
    # and pandas trimming numbers by default.
    new_postal: list[str] = []
    for _ in range(5 - len(postal)):
        new_postal.append("0")
    
    new_postal.extend(postal)

    return "".join(new_postal)

def is_canada_postal(postal: str) -> bool:
    '''Checks if the postal is Canada based. If the postal is valid, then it will
    return True, otherwise it will return False.

    Valid postals: `A1A1A1`, `A1A 1A1`
    '''
    letter_count: int = 0
    number_count: int = 0
    for c in postal:
        if c.isalpha():
            letter_count += 1
        if c.isnumeric():
            number_count += 1

    if len(postal) not in [6, 7] or letter_count != 3 or number_count != 3:
        return False
    
    return True

def convert_country_to_full(country: str) -> str:
    '''Checks if the country is abbreviated and returns the full name.
    This supports Canada and US only.
    '''
    country = country.lower()
    us_abbrev: set[str] = {"us", "usa", "america"}
    ca_abbrev: set[str] = {"ca", "can"}

    us: str = "United States"
    ca: str = "Canada"

    if country in us_abbrev:
        return us 
    elif country in ca_abbrev: 
        return ca
    
    return country.title()