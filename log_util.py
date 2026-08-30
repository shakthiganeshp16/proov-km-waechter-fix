# log_util.py
# Homemade logger for Vossberg Mobility fleet tooling.

import time

LOG_LINES: list = []   # global buffer, flushed to disk by flush_log()
DEBUG = False          # has been False since 2014; dead branch removed below


def log(message: str) -> None:
    """Timestamp and buffer a log line, and echo it to stdout."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def debug(message: str) -> None:
    """Log a debug message — only active when DEBUG is True."""
    if DEBUG:
        log(f"DEBUG: {message}")


def flush_log(path: str) -> None:
    """Append all buffered log lines to the given file and clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
