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

DATE_STRING: str = datetime.now().strftime("%Y-%m-%d")
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
    file_name: str = "",
    log_path: Path | str = None,
    log_level: LogLevel = "debug",
    handler_levels: HandlerLevelOptions = {},
    stream: TextIO = sys.stdout,
    logfmt: str = "%(asctime)s:%(filename)s:%(name)s [%(levelname)s] %(message)s",
    datefmt: str = DEFAULT_DATEFMT):
        '''Create a new logging instance.
        
        Parameters
        ----------
            name: str
                The name of the logger. By default, it uses the __name__ variable, or
                in other words __main__.
            
            file_name: str
                The log file name. This is attached to a date and the format will follow
                `YYYY-MM-DD.<file_name>.log`. By default it is an empty string. If `log_path`
                is `None`, then this will do nothing.
            
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

        self._stream_handler: StreamHandler = StreamHandler(stream)
        # will default to stdout if None
        self._file_handler: FileHandler = None

        self.formatter: Formatter = Formatter(fmt=logfmt, datefmt=datefmt)

        self.log_level: LogLevel = log_level
        self.log_levels_obj: LogLevels = {
            "debug": DEBUG,
            "info": INFO,
            "warning": WARNING,
            "error": ERROR,
            "critical": CRITICAL,
        }

        # creates the log path
        self._log_file: Path = log_path
        if log_path is not None:
            new_log_path: Path = Path("")
            if isinstance(log_path, str):
                new_log_path = Path(log_path)
            elif isinstance(log_path, Path):
                new_log_path = log_path
            
            if not new_log_path.exists():
                new_log_path.mkdir(parents=True, exist_ok=True)

            file_name = file_name.strip()
            if file_name != "":
                file_name = "." + file_name
            self._log_file = new_log_path / f"{DATE_STRING}{file_name}.log"
            self._file_handler = FileHandler(self._log_file)

        hdlrs: list[Handler] = [self._stream_handler]
        hdlr_levels: list[int] = [
            self.log_levels_obj.get(
                handler_levels.get("stream_level", DEBUG), DEBUG
            )
        ]

        if self._file_handler is not None:
            hdlrs.append(self._file_handler)
            hdlr_levels.append(
                self.log_levels_obj.get(
                    handler_levels.get("file_level", DEBUG), 
                    DEBUG
                )
            )
        
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
    
    def set_stream_level(self, level: LogLevel) -> None:
        '''Sets the log level of the stream handler.'''
        level = level.lower()
        self._stream_handler.setLevel(self.log_levels_obj[level])
    
    def _set_handlers(self, handlers: list[Handler], levels: list[LogLevel]) -> None:
        '''Sets the handlers and their logging level.'''
        for i, handler in enumerate(handlers):
            level: LogLevel = levels[i]

            handler.setFormatter(self.formatter)
            handler.setLevel(level)

            self.addHandler(handler)
        
    @property
    def log_file(self) -> Path | None:
        '''The log file path. If a log path was not given, then return None.'''
        return self._log_file