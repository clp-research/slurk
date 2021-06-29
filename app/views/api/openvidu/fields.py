import marshmallow as ma
from marshmallow import ValidationError

from app.models.room import Session


class SessionId(ma.fields.String):
    def _validate(self, value):
        from flask.globals import current_app
        super()._validate(value)
        if current_app.session.query(Session).get(value) is None:
            raise ValidationError(f'Session `{value}` does not exist')


class List(ma.fields.List):
    def _serialize(self, value, attr, obj, **kwargs):
        return super()._serialize(value['content'], attr, obj, **kwargs)


class String(ma.fields.String):
    def _serialize(self, value, attr, obj, **kwargs):
        return super()._serialize(value if value != '' else None, attr, obj, **kwargs)


class Timestamp(ma.fields.DateTime):
    def _serialize(self, value, attr, obj, **kwargs):
        from datetime import datetime
        return super()._serialize(datetime.fromtimestamp(value / 1000.0) if value is not None else None, attr, obj, **kwargs)
