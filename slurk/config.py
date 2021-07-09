import os
import random
import string


def environ_as_boolean(env, default):
    var = os.environ.get(env)
    if var is None:
        return default
    return var.lower() in ("y", "ye", "yeah", "yes", "true", "1", "on")


# Server config
DEBUG = environ_as_boolean(
    "SLURK_DEBUG", default=os.environ.get("FLASK_ENV") == "development"
)

SECRET_KEY = os.environ.get(
    "SLURK_SECRET_KEY",
    "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32)),
)
DATABASE = os.environ.get("SLURK_DATABASE_URI", "sqlite:///:memory:")

if "SLURK_OPENVIDU_URL" in os.environ:
    OPENVIDU_URL = os.environ["SLURK_OPENVIDU_URL"]
    OPENVIDU_SECRET = os.environ.get("SLURK_OPENVIDU_SECRET")
    OPENVIDU_PORT = int(os.environ.get("SLURK_OPENVIDU_PORT", default="443"))
    OPENVIDU_VERIFY = environ_as_boolean("SLURK_OPENVIDU_VERIFY", default=True)

API_TITLE = "slurk"
API_VERSION = "v3"
OPENAPI_VERSION = "3.0.2"
OPENAPI_JSON_PATH = "api-spec.json"
OPENAPI_URL_PREFIX = "/"
OPENAPI_REDOC_PATH = "/redoc"
OPENAPI_REDOC_URL = (
    "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
)
OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
OPENAPI_RAPIDOC_PATH = "/rapidoc"
OPENAPI_RAPIDOC_URL = "https://cdn.jsdelivr.net/npm/rapidoc/dist/rapidoc-min.js"
OPENAPI_RAPIDOC_CONFIG = {
    "render-style": "view",
    "schema-style": "table",
    "schema-description-expanded": "true",
}
