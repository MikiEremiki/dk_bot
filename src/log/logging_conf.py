import pathlib
import os
import logging.handlers

from rich.console import Console
from rich.highlighter import Highlighter
from rich.logging import RichHandler
from rich.traceback import install, Traceback

log_folder_name = 'archive'
log_filename = 'bot.log'
postgres_log_filename = 'postgres.log'

parent_dir = pathlib.Path(__file__).parent
absolute_path = pathlib.Path(
    pathlib.Path.joinpath(parent_dir, log_folder_name))
LOG_FILENAME = pathlib.Path(
    pathlib.Path.joinpath(absolute_path, log_filename))
POSTGRES_LOG_FILENAME = pathlib.Path(
    pathlib.Path.joinpath(absolute_path, postgres_log_filename))
if not absolute_path.exists():
    os.mkdir(log_folder_name)

fmt = '{levelname} | {name}:{lineno}:{funcName} | module={module}'
bf = logging.Formatter(fmt, style='{')
log_time_format = '%Y-%m-%d %H:%M:%S'
width = 150


class ModuleExclusionFilter(logging.Filter):
    def __init__(self, excluded_module_name):
        super().__init__()
        self.excluded_module_name = excluded_module_name

    def filter(self, record):
        return self.excluded_module_name not in record.name


sql_alchemy_filter = ModuleExclusionFilter('sqlalchemy.engine')


class MyHighlighter(Highlighter):
    def highlight(self, text):
        text.stylize('bold red', 0, len(text))


class RotatingRichFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console(file=self.stream,
                               highlighter=MyHighlighter(),
                               log_time_format=log_time_format,
                               log_path=False,
                               width=width)

    def emit(self, record):
        try:
            if self.shouldRollover(record):
                self.doRollover()
                self.console = Console(file=self.stream,
                                       highlighter=MyHighlighter(),
                                       log_time_format=log_time_format,
                                       log_path=False,
                                       width=width)

            msg = self.format(record)
            self.console.log(msg)
            if record.exc_info:
                exc_type, exc_value, exc_tb = record.exc_info
                tb = Traceback.from_exception(
                    exc_type,
                    exc_value,
                    exc_tb,
                    width=width,
                    show_locals=True,
                    max_frames=10
                )
                self.console.print('TRACEBACK')
                self.console.print(tb)
            else:
                if hasattr(record.msg, 'model_dump'):
                    record.msg = record.msg.model_dump()
                if isinstance(record.msg, str):
                    self.console.print(record.message)
                else:
                    self.console.print(record.msg)
            self.flush()
        except Exception:
            self.handleError(record)


def load_log_config():
    install(console=Console(), max_frames=4, width=None)
    rich_handler = RichHandler(
        console=Console(width=width),
        log_time_format=log_time_format
    )
    rich_handler.addFilter(sql_alchemy_filter)

    main_log_file_handler = RotatingRichFileHandler(LOG_FILENAME,
                                                    maxBytes=1024000,
                                                    backupCount=5,
                                                    encoding='utf-8')
    main_log_file_handler.setFormatter(bf)
    main_log_file_handler.addFilter(sql_alchemy_filter)

    postgres_log_file_handler = RotatingRichFileHandler(
        POSTGRES_LOG_FILENAME,
        maxBytes=2048000,
        backupCount=10,
        encoding='utf-8')
    postgres_log_file_handler.setFormatter(bf)

    root = logging.getLogger()
    root.setLevel('DEBUG')

    root.addHandler(rich_handler)
    root.addHandler(main_log_file_handler)

    logger_postgres = logging.getLogger('sqlalchemy.engine')
    logger_postgres.setLevel('INFO')
    logger_postgres.addHandler(postgres_log_file_handler)

    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)
    return logger
