import logging

"""Set the logging level.

logger.set_level(level: str)

Args:
    level (str): The logging level to set. Options are 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
"""

logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG to see debug messages
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)
