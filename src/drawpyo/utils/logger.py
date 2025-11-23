import logging

logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG to see debug messages
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)