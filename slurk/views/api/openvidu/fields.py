import marshmallow as ma
from marshmallow import ValidationError

from slurk.models.room import Session


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


class IntegerOrNone(ma.fields.Integer):
    def __init__(self, *, strict=False, **kwargs):
        kwargs['allow_none'] = True
        super().__init__(strict=strict, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        return super()._serialize(value if value != 0 else None, attr, obj, **kwargs)


class Resolution(ma.fields.String):
    def _validate(self, value):
        super()._validate(value)
        res = value.split('x')
        if len(res) != 2:
            raise ValidationError('Invalid resolution string. Must be `WIDTHxHEIGHT`')
        try:
            w = int(res[0])
        except ValueError as e:
            raise ValidationError(f'Invalid width: {e}')
        try:
            h = int(res[1])
        except ValueError as e:
            raise ValidationError(f'Invalid height: {e}')
        if w < 100 or w > 1999:
            raise ValidationError('Invalid width: Must be >= 100 and <= 1999')
        if h < 100 or h > 1999:
            raise ValidationError('Invalid height: Must be >= 100 and <= 1999')


class Timestamp(ma.fields.DateTime):
    def _serialize(self, value, attr, obj, **kwargs):
        from datetime import datetime
        return super()._serialize(datetime.fromtimestamp(value / 1000.0) if value is not None else None, attr, obj, **kwargs)
