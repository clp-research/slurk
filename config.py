import os
import logging


def environ_as_boolean(env, default):
    var = os.environ.get(env)
    if var is None:
        return default
    return var.lower() in ("y", "ye", "yeah", "yes", "true", "1", "on")


# Server config
DEBUG = environ_as_boolean("DEBUG", default=False)
if DEBUG:
    class NoPing(logging.Filter):
        def filter(self, record):
            message = record.getMessage().lower()
            return 'ping' not in message and 'pong' not in message

    eio_logger = logging.getLogger("engineio.server")
    eio_logger.setLevel(logging.DEBUG)
    eio_logger.addFilter(NoPing())
    logging.getLogger("socketio.server").addFilter(NoPing())
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("slurk").setLevel(logging.DEBUG)

SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
DATABASE = os.environ.get("DATABASE", default=None)
if DATABASE == 'sqlite:///' or DATABASE == 'sqlite:///:memory:':
    logging.getLogger("slurk").error(
        "Using the memory as database is not supported. Pass an URI with `DATABASE` as environment variable or define it in `config.py`.")
