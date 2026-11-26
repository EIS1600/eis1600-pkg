"""Helpers to route recogniser warnings to the terminal and a log file.

The recogniser emits advisory warnings (e.g. a day beyond its month's length,
via the ``temporal_entity_recogniser.validation`` logger). These helpers attach
handlers so those warnings are written to the console and/or a timestamped file
under ``src/_logs`` (a sibling of this package).
"""
import logging
from datetime import datetime
from pathlib import Path

# Default log directory: src/_logs (this package's parent's sibling).
DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / '_logs'

_PKG = 'temporal_entity_recogniser'
_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'


def new_log_path(log_dir=None) -> Path:
    """Return a fresh timestamped log-file path, creating *log_dir* if needed."""
    log_dir = Path(log_dir) if log_dir is not None else DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f'{_PKG}_{datetime.now():%Y%m%d_%H%M%S_%f}.log'


def configure_logging(log_dir=None, console=True, log_path=None) -> Path:
    """Send package warnings to a log file (and, by default, the console).

    Returns the log-file path. Idempotent: handlers added by a previous call are
    removed first.
    """
    if log_path is None:
        log_path = new_log_path(log_dir)
    log_path = Path(log_path)

    pkg = logging.getLogger(_PKG)
    pkg.setLevel(logging.WARNING)
    pkg.propagate = False
    for handler in [h for h in pkg.handlers if getattr(h, '_ter_managed', False)]:
        pkg.removeHandler(handler)

    fmt = logging.Formatter(_FORMAT)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(fmt)
    file_handler._ter_managed = True
    pkg.addHandler(file_handler)
    if console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt)
        stream_handler._ter_managed = True
        pkg.addHandler(stream_handler)
    return log_path


def configure_worker_logging(log_path) -> None:
    """Logging setup for a batch worker process (file only).

    Silences the noisy per-record recognition warnings but keeps the validation
    warnings, appending them to the shared *log_path*.
    """
    logging.getLogger(f'{_PKG}.recogniser').setLevel(logging.ERROR)
    pkg = logging.getLogger(_PKG)
    pkg.setLevel(logging.WARNING)
    pkg.propagate = False
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(_FORMAT))
    pkg.addHandler(file_handler)
