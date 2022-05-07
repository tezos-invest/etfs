import os

import dotenv

dotenv.load_dotenv()

CONTRACT_ADDRESS= {
    'hangzhou': 'KT18q4si6YmzJjbgZ3wV7HYfds1E3EbD7tBx'
}

TZKT_ENDPOINT = os.getenv("TZKT_ENDPOINT", "hangzhou")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
DEBUG = os.getenv("DEBUG", False)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "stderr": {
            "level": LOGGING_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["stderr"],
            "level": "DEBUG",
        },
    },
}
