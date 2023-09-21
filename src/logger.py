"""Logging Configuration"""

from logging import getLogger, basicConfig
from config import LOGGING_LEVEL

basicConfig(
    format="%(asctime)s %(message)s",
    encoding="utf-8",
    datefmt="%Y-%m-%dT%H:%M:%S%z",  # 1996-12-19T16:39:57-08:00
    level=LOGGING_LEVEL,
)
logger = getLogger(__name__)
