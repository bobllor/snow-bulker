from pathlib import Path
from src.core.yaml.data_yaml.data_yaml_loader import DataYamlLoader
from src.core.yaml.html_yaml.html_yaml_loader import HTMLYamlLoader
from src.core.yaml.config_yaml.config_yaml_loader import ConfigYamlLoader, Config
from src.core.yaml.yaml_loader import YamlStarter, ParsedYaml
from src.core.bulker import Bulker
from src.support.types import Result
from src.core.runner import Runner
from logger import Log, LogLevel
from src.core.program_start import ProgramStarter
from typing import TypedDict
import src.support.utils as utils

class SettingsObj(TypedDict):
    log_level: LogLevel
    headless: bool

if __name__ == "__main__":
    project_root: Path = Path(__file__).parent
    DATA_FILE: str = "data"
    HTML_FILE: str = "html"
    CONFIG_FILE: str = "config"

    yaml_extensions: list[str] = ["yml", "yaml"]

    config_loader: ConfigYamlLoader = ConfigYamlLoader()
    config: Config = utils.get_config(project_root, CONFIG_FILE, yaml_extensions, config_loader)

    logger: Log = Log(
        log_path=config.settings.log_folder,
        handler_levels={
            "stream_level": config.settings.stream_log_level
        },
    )

    data_loader: DataYamlLoader = DataYamlLoader(logger=logger)
    html_loader: HTMLYamlLoader = HTMLYamlLoader(logger=logger)
    # reinit from the config
    config_loader = ConfigYamlLoader(logger=logger)

    # config and HTML files are case sensitive, they must be lowered
    # this is handeled inside ProgramStarter.parse_yaml
    yaml_objs: list[YamlStarter] = [
        {"yaml_loader": data_loader, "data_file": DATA_FILE, "parsed_key": "excel_root"},
        {"yaml_loader": html_loader, "data_file": HTML_FILE, "parsed_key": "html_fields"},
        {"yaml_loader": config_loader, "data_file": CONFIG_FILE, "parsed_key": "config"}
    ]

    quit_str: str = "q"
    start_str: str = "s"
    runner: Runner = Runner(quit_str)

    menu_txt: list[str] = [
        "Start",
        "Quit"
    ]

    choices: list[str] = [start_str, quit_str]
    # used to display messages above the menu
    banner: str = ""
    run_count: int = 1
    
    while True:
        starter: ProgramStarter = ProgramStarter(project_root, logger=logger)

        try:
            runner.clear()
            option: str = runner.menu(menu_txt=menu_txt, choices=choices, banner_txt=banner)

            if option == runner.quit_str:
                exit(0)
            elif option == start_str:
                runner.clear()
                res: Result[ParsedYaml] = starter.parse_yaml(yaml_objs, yaml_extensions)
                if res.err:
                    logger.error(res.msg)

                    runner.enter_to_continue()

                    continue

                yaml_content: ParsedYaml = res.content
                hot_config: Config = res.content["config"]

                invalid_keys: list[str] = config_loader.check_empty(dict(hot_config))
                if len(invalid_keys) > 0:
                    logger.error(
                        f"The following keys have invalid values or are missing, correction required: \n- {"\n- ".join(invalid_keys)}"
                    )

                    runner.enter_to_continue()

                    continue
                
                if hot_config.settings.log_level != config.settings.log_level:
                    logger = Log(
                        log_path=config.settings.log_folder,
                        handler_levels={
                            "stream_level": config.settings.stream_log_level
                        },
                    )

                logger.debug(f"Config program settings: {hot_config.settings}")
                bulker: Bulker = Bulker(
                    project_root, 
                    data_folder=hot_config.settings.data_folder, 
                    logger=logger
                )
                starter.start(
                    bulker, 
                    yaml_content["config"], 
                    yaml_content["excel_root"],
                    yaml_content["html_fields"], 
                    headless=hot_config.settings.headless,
                )

                # update config to the new loaded hot_config
                config = hot_config
                runner.enter_to_continue()

                # TODO: display the final result with the automation, this requires
                # a new value to be propagated up, a global variable, or some class.
                banner = f"Completed bulk #{run_count}"
                run_count += 1
            else:
                banner = f"Unrecognized option '{option}'"

                # dont display an empty string.
                if option == "":
                    banner = ""
        except Exception as e:
            banner = "An unknown error has occurred, it has been logged"
            logger.critical(f"Unknown exception occurred: {e}")

            runner.enter_to_continue()
        except KeyboardInterrupt:
            # this doesnt exit the chrome browser if the driver is in a waiting period. 
            # will have to look into it further but it doesnt look like its possible.
            starter.quit_driver()
            exit(0)
        finally:
            starter.quit_driver()