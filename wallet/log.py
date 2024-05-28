import logging

from colors import COLORS

logging.basicConfig(
    format=f"[{COLORS['CYAN']}%(levelname)s{COLORS['WHITE']}][{COLORS['PURPLE']}%(asctime)s{COLORS['WHITE']}][{COLORS['YELLOW']}%(filename)-15s{COLORS['WHITE']}]{COLORS['DARK_GRAY']}[%(lineno)4d][%(name)10s]{COLORS['WHITE']} - %(message)s",
    level=logging.INFO,
    force=True,
)


def get_logger(name): # pragma: no cover
    logger = logging.getLogger(name)
    return logger
