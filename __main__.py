import logging.config

import uvicorn

import config
from api import app

if __name__ == "__main__":
    logging.config.dictConfig(config.LOGGING)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        debug=config.DEBUG,
        log_config=config.LOGGING,
    )
