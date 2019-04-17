from werkzeug.utils import import_string


class Settings:
    secret_key = None
    debug = False
    database_url = None

    @classmethod
    def from_object(cls, obj):
        if isinstance(obj, str):
            obj = import_string(obj)

        cls.secret_key = getattr(obj, "SECRET_KEY")
        cls.debug = getattr(obj, "DEBUG")
        cls.database_url = getattr(obj, "SQLALCHEMY_DATABASE_URI")

        return cls
