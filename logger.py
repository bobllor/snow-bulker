from logging import Logger, Formatter, StreamHandler, FileHandler, Handler, setLoggerClass
from logging import (
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL
)
from datetime import datetime
from typing import TypedDict, Literal, TextIO, Any
from pathlib import Path
import sys

# this value will be the same as soon as the server is launched.
# this keeps all logs in one day on the same day.
DEFAULT_FILENAME: datetime = datetime.now().strftime("bulker-%Y-%m-%d.log")
DEFAULT_DATEFMT: Literal["%Y-%m-%d %H:%M:%S"] = "%Y-%m-%d %H:%M:%S"

LogLevel = Literal["debug", "info", "error", "warning", "critical"]
class LogLevels(TypedDict):
    debug: int
    info: int
    error: int
    warning: int
    critical: int

class HandlerLevelOptions(TypedDict):
    stream_level: LogLevel
    file_level: LogLevel

class Log(Logger):
    def __init__(self, 
    name: str = __name__,
    *, 
    log_dir: Path | str = None,
    log_level: LogLevel = "debug",
    handler_levels: HandlerLevelOptions = {},
    stream: TextIO = sys.stdout,
    logfmt: str = "%(asctime)s:%(filename)s:%(name)s [%(levelname)s] %(message)s",
    datefmt: str = DEFAULT_DATEFMT):
        '''Create a new logging instance.
        
        Parameters
        ----------
            name: str default __name__
                The name of the logger. By default, it uses the __name__ variable, or
                in other words __main__.
            
            log_path: Path | str, default None
                The path to the log directory. By default it is None, meaning it will not write a log file.
                If a path is given, then the output of the log file will be to the given directory.

            log_level: LogLevel
                Used for the logging level. By default it is `debug`.

            handler_levels: HandlerLevelOptions default {}
                A dictionary that holds the logging levels of the stream and file handler.
                By default *all levels are DEBUG*.
            
            stream: TextIO default sys.stdout
                The stream output of the StreamHandler. By default it prints out to the console, sys.stdout.
            
            logfmt: str default TIME FILENAME LOGNAME [LEVEL] MESSAGE
                The format of the log message.
        
            datefmt: str default YY-MM-DD HH-MM-SS
                The format for the date.
        '''
        super().__init__(name)

        stream_handler: StreamHandler = StreamHandler(stream)
        # will default to stdout if None
        file_handler: FileHandler = None

        self.formatter: Formatter = Formatter(fmt=logfmt, datefmt=datefmt)

        self.log_level: LogLevel = log_level
        self.log_levels_obj: LogLevels = {
            "debug": DEBUG,
            "info": INFO,
            "warning": WARNING,
            "error": ERROR,
            "critical": CRITICAL,
        }

        # creates the log directory and path
        if log_dir is not None:
            new_log_dir: Path = Path("")
            if isinstance(log_dir, str):
                new_log_dir = Path(log_dir)
            elif isinstance(log_dir, Path):
                new_log_dir = log_dir
            
            if not new_log_dir.exists():
                new_log_dir.mkdir(parents=True, exist_ok=True)

            log_file: Path = new_log_dir / DEFAULT_FILENAME
            file_handler = FileHandler(log_file)

        hdlrs: list[Handler] = [stream_handler]
        hdlr_levels: list[int] = [
            self.log_levels_obj.get(
                handler_levels.get("stream_level", DEBUG), DEBUG
            )
        ]

        if file_handler is not None:
            hdlrs.append(file_handler)
            hdlr_levels.append(self.log_levels_obj.get(handler_levels.get("file_level", DEBUG)))
        
        self._set_handlers(hdlrs, hdlr_levels)

        self.setLevel(self.log_levels_obj.get(log_level, DEBUG))

    
    def create_dict(self, **kwargs) -> dict[str, Any]:
        '''Generates a dictionary with any keyword arguments.'''
        return {
            **kwargs
        }
    
    def set_logger(self) -> None:
        '''Sets the Log for the logger class for module-level use.'''
        setLoggerClass(Log) 
    
    def _set_handlers(self, handlers: list[Handler], levels: list[LogLevel]) -> None:
        '''Sets the handlers and their logging level.'''
        for i, handler in enumerate(handlers):
            level: LogLevel = levels[i]

            handler.setFormatter(self.formatter)
            handler.setLevel(level)

            self.addHandler(handler)