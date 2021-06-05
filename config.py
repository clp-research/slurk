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

API_TITLE = "slurk"
API_VERSION = "v3"
OPENAPI_VERSION = "3.0.2"
OPENAPI_JSON_PATH = "api-spec.json"
OPENAPI_URL_PREFIX = "/"
OPENAPI_REDOC_PATH = "/redoc"
OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
OPENAPI_RAPIDOC_PATH = "/rapidoc"
OPENAPI_RAPIDOC_URL = "https://cdn.jsdelivr.net/npm/rapidoc/dist/rapidoc-min.js"
OPENAPI_RAPIDOC_CONFIG = {
    'render-style': 'view',
    'schema-style': 'table',
}

SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
if 'DATABASE' in os.environ:
    DATABASE = os.environ['DATABASE']

    if DATABASE == 'sqlite:///' or DATABASE == 'sqlite:///:memory:':
        logging.getLogger("slurk").error(
            "Using the memory as database is not supported. Pass an URI with `DATABASE` as environment variable or define it in `config.py`.")
