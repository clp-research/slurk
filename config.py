import os


def environ_as_boolean(env, default=False):
    var = os.environ.get(env)
    if var is None:
        return default
    return var.lower() not in ("f", "false", "0", "no", "off")


# Server config
DEBUG = environ_as_boolean("DEBUG", default=False)

SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set for application")


# SQLAlchemy config
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", default="sqlite:///:memory:")
SQLALCHEMY_TRACK_MODIFICATIONS = environ_as_boolean("DATABASE_TRACK_MODIFICATIONS", default=False)
SQLALCHEMY_ECHO = environ_as_boolean("DATABASE_ECHO", default=False)
