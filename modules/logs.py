import io, logging, os, re, sys, traceback
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
COLLECTION_DIR = "collections"
PLAYLIST_DIR = "playlists"
MAIN_LOG = "meta.log"
LIBRARY_LOG = "library.log"
COLLECTION_LOG = "collection.log"
PLAYLIST_LOG = "playlist.log"
PLAYLISTS_LOG = "playlists.log"

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10


def fmt_filter(record):
    record.levelname = f"[{record.levelname}]"
    record.filename = f"[{record.filename}:{record.lineno}]"
    return True

_srcfile = os.path.normcase(fmt_filter.__code__.co_filename)


class MyLogger:
    def __init__(self, logger_name, default_dir, screen_width, separating_character, ignore_ghost, is_debug):
        self.logger_name = logger_name
        self.default_dir = default_dir
        self.screen_width = screen_width
        self.separating_character = separating_character
        self.is_debug = is_debug
        self.ignore_ghost = ignore_ghost
        self.log_dir = os.path.join(default_dir, LOG_DIR)
        self.playlists_dir = os.path.join(self.log_dir, PLAYLIST_DIR)
        self.main_log = os.path.join(self.log_dir, MAIN_LOG)
        self.main_handler = None
        self.save_errors = False
        self.saved_errors = []
        self.library_handlers = {}
        self.collection_handlers = {}
        self.playlist_handlers = {}
        self.playlists_handler = None
        self.secrets = []
        self.spacing = 0
        self.playlists_log = os.path.join(self.playlists_dir, PLAYLISTS_LOG)
        os.makedirs(self.log_dir, exist_ok=True)
        self._logger = logging.getLogger(self.logger_name)
        self._logger.setLevel(logging.DEBUG)

        cmd_handler = logging.StreamHandler()
        cmd_handler.setLevel(logging.DEBUG if self.debug else logging.INFO)

        self._logger.addHandler(cmd_handler)

    def clear_errors(self):
        self.saved_errors = []

    def _get_handler(self, log_file, count=3):
        _handler = RotatingFileHandler(log_file, delay=True, mode="w", backupCount=count, encoding="utf-8")
        self._formatter(_handler)
        if os.path.isfile(log_file):
            _handler.doRollover()
        return _handler

    def _formatter(self, handler, border=True):
        text = f"| %(message)-{self.screen_width - 2}s |" if border else f"%(message)-{self.screen_width - 2}s"
        if isinstance(handler, RotatingFileHandler):
            text = f"[%(asctime)s] %(filename)-27s %(levelname)-10s {text}"
        handler.setFormatter(logging.Formatter(text))

    def add_main_handler(self):
        self.main_handler = self._get_handler(self.main_log, count=10)
        self.main_handler.addFilter(fmt_filter)
        self._logger.addHandler(self.main_handler)

    def remove_main_handler(self):
        self._logger.removeHandler(self.main_handler)

    def add_library_handler(self, library_key):
        os.makedirs(os.path.join(self.log_dir, library_key, COLLECTION_DIR), exist_ok=True)
        self.library_handlers[library_key] = self._get_handler(os.path.join(self.log_dir, library_key, LIBRARY_LOG))
        self._logger.addHandler(self.library_handlers[library_key])

    def remove_library_handler(self, library_key):
        if library_key in self.library_handlers:
            self._logger.removeHandler(self.library_handlers[library_key])

    def re_add_library_handler(self, library_key):
        if library_key in self.library_handlers:
            self._logger.addHandler(self.library_handlers[library_key])

    def add_playlists_handler(self):
        os.makedirs(self.playlists_dir, exist_ok=True)
        self.playlists_handler = self._get_handler(self.playlists_log, count=10)
        self._logger.addHandler(self.playlists_handler)

    def remove_playlists_handler(self):
        self._logger.removeHandler(self.playlists_handler)

    def add_collection_handler(self, library_key, collection_key):
        collection_dir = os.path.join(self.log_dir, str(library_key), COLLECTION_DIR, str(collection_key))
        os.makedirs(collection_dir, exist_ok=True)
        if library_key not in self.collection_handlers:
            self.collection_handlers[library_key] = {}
        self.collection_handlers[library_key][collection_key] = self._get_handler(os.path.join(collection_dir, COLLECTION_LOG))
        self._logger.addHandler(self.collection_handlers[library_key][collection_key])

    def remove_collection_handler(self, library_key, collection_key):
        if library_key in self.collection_handlers and collection_key in self.collection_handlers[library_key]:
            self._logger.removeHandler(self.collection_handlers[library_key][collection_key])

    def add_playlist_handler(self, playlist_key):
        playlist_dir = os.path.join(self.playlists_dir, playlist_key)
        os.makedirs(playlist_dir, exist_ok=True)
        self.playlist_handlers[playlist_key] = self._get_handler(os.path.join(playlist_dir, PLAYLIST_LOG))
        self._logger.addHandler(self.playlist_handlers[playlist_key])

    def remove_playlist_handler(self, playlist_key):
        if playlist_key in self.playlist_handlers:
            self._logger.removeHandler(self.playlist_handlers[playlist_key])

    def _centered(self, text, sep=" ", side_space=True, left=False):
        if len(text) > self.screen_width - 2:
            return text
        space = self.screen_width - len(text) - 2
        text = f"{' ' if side_space else sep}{text}{' ' if side_space else sep}"
        if space % 2 == 1:
            text += sep
            space -= 1
        side = int(space / 2) - 1
        final_text = f"{text}{sep * side}{sep * side}" if left else f"{sep * side}{text}{sep * side}"
        return final_text

    def separator(self, text=None, space=True, border=True, debug=False, side_space=True, left=False):
        sep = " " if space else self.separating_character
        for handler in self._logger.handlers:
            self._formatter(handler, border=False)
        border_text = f"|{self.separating_character * self.screen_width}|"
        if border and debug:
            self.debug(border_text)
        elif border:
            self.info(border_text)
        if text:
            text_list = text.split("\n")
            for t in text_list:
                if debug:
                    self.debug(f"|{sep}{self._centered(t, sep=sep, side_space=side_space, left=left)}{sep}|")
                else:
                    self.info(f"|{sep}{self._centered(t, sep=sep, side_space=side_space, left=left)}{sep}|")
            if border and debug:
                self.debug(border_text)
            elif border:
                self.info(border_text)
        for handler in self._logger.handlers:
            self._formatter(handler)

    def debug(self, msg, *args, **kwargs):
        if self._logger.isEnabledFor(DEBUG):
            self._log(DEBUG, str(msg), args, **kwargs)

    def info_center(self, msg, *args, **kwargs):
        self.info(self._centered(str(msg)), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self._logger.isEnabledFor(INFO):
            self._log(INFO, str(msg), args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self._logger.isEnabledFor(WARNING):
            self._log(WARNING, str(msg), args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.save_errors:
            self.saved_errors.append(msg)
        if self._logger.isEnabledFor(ERROR):
            self._log(ERROR, str(msg), args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.save_errors:
            self.saved_errors.append(msg)
        if self._logger.isEnabledFor(CRITICAL):
            self._log(CRITICAL, str(msg), args, **kwargs)

    def stacktrace(self):
        self.debug(traceback.format_exc())

    def _space(self, display_title):
        display_title = str(display_title)
        space_length = self.spacing - len(display_title)
        if space_length > 0:
            display_title += " " * space_length
        return display_title

    def ghost(self, text):
        if not self.ignore_ghost:
            try:
                final_text = f"| {text}"
            except UnicodeEncodeError:
                text = text.encode("utf-8")
                final_text = f"| {text}"
            print(self._space(final_text), end="\r")
            self.spacing = len(text) + 2

    def exorcise(self):
        if not self.ignore_ghost:
            print(self._space(" "), end="\r")
            self.spacing = 0

    def secret(self, text):
        if str(text) not in self.secrets:
            self.secrets.append(str(text))

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        if self.spacing > 0:
            self.exorcise()
        if "\n" in msg:
            for i, line in enumerate(msg.split("\n")):
                self._log(level, line, args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)
                if i == 0:
                    for handler in self._logger.handlers:
                        if isinstance(handler, RotatingFileHandler):
                            handler.setFormatter(logging.Formatter(" " * 65 + "| %(message)s"))
            for handler in self._logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    handler.setFormatter(logging.Formatter("[%(asctime)s] %(filename)-27s %(levelname)-10s | %(message)s"))
        else:
            for secret in self.secrets:
                if secret in msg:
                    msg = msg.replace(secret, "(redacted)")
            if "HTTPConnectionPool" in msg:
                msg = re.sub("HTTPConnectionPool\\((.*?)\\)", "HTTPConnectionPool(redacted)", msg)
            if "HTTPSConnectionPool" in msg:
                msg = re.sub("HTTPSConnectionPool\\((.*?)\\)", "HTTPSConnectionPool(redacted)", msg)
            try:
                if not _srcfile:
                    raise ValueError
                fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
            except ValueError:
                fn, lno, func, sinfo = "(unknown file)", 0, "(unknown function)", None
            if exc_info:
                if isinstance(exc_info, BaseException):
                    exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
                elif not isinstance(exc_info, tuple):
                    exc_info = sys.exc_info()
            record = self._logger.makeRecord(self._logger.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
            self._logger.handle(record)

    def findCaller(self, stack_info=False, stacklevel=1):
        f = logging.currentframe()
        if f is not None:
            f = f.f_back
        orig_f = f
        while f and stacklevel > 1:
            f = f.f_back
            stacklevel -= 1
        if not f:
            f = orig_f
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        return rv
