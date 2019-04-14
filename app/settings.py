from werkzeug.utils import import_string


class Settings:
    secret_key = None

    @classmethod
    def from_object(cls, obj):
        if isinstance(obj, str):
            obj = import_string(obj)

        cls.secret_key = getattr(obj, "SECRET_KEY")

        return cls
