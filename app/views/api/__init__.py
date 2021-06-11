import marshmallow as ma
from flask.globals import current_app
from marshmallow.exceptions import ValidationError

from marshmallow_sqlalchemy import SQLAlchemySchemaOpts, auto_field


def register_blueprints(api):
    from . import layouts, logs, permissions, tokens, users, tasks, rooms

    MODULES = (
        layouts,
        rooms,
        permissions,
        tokens,
        users,
        tasks,
        logs,
    )

    for module in MODULES:
        name = module.__name__.split('.')[-1]
        api.register_blueprint(module.blp, url_prefix=f'/slurk/api/{name}')


class Id(ma.fields.Integer):
    def __init__(self, *, table, **kwargs):
        self._table = table
        super().__init__(strict=False, **kwargs)

    def _validated(self, value):
        from flask.globals import current_app
        id = super()._validated(value)
        if current_app.session.query(self._table).get(id) is None:
            raise ValidationError(f'{self._table.__tablename__} `{id}` does not exist')
        return id


class BaseOpts(SQLAlchemySchemaOpts):
    def __init__(self, meta, *args, **kwargs):
        meta.unknown = ma.RAISE
        meta.ordered = True
        super().__init__(meta)


class CommonSchema(ma.Schema):
    OPTIONS_CLASS = BaseOpts

    id = auto_field(dump_only=True, metadata={'description': 'Unique ID that identifies this entity'})
    date_created = auto_field(dump_only=True, metadata={'description': 'Server time at which this entity was created'})
    date_modified = auto_field(
        dump_only=True, metadata={
            'description': 'Server time when this entity was last modified'})

    def list(self, args):
        return current_app.session.query(self.Meta.model) \
            .filter_by(**args) \
            .order_by(self.Meta.model.date_created.desc()) \
            .all()

    def post(self, item):
        if isinstance(item, self.Meta.model):
            entity = item
        else:
            entity = self.Meta.model(**item)
        db = current_app.session
        db.add(entity)
        db.commit()
        return entity

    def put(self, old, new):
        if isinstance(new, self.Meta.model):
            entity = new
        else:
            entity = self.Meta.model(**new)
        loadable_fields = [k for k, v in self.fields.items() if not v.dump_only]
        for name in loadable_fields:
            setattr(old, name, getattr(entity, name, None))
        current_app.session.commit()
        return old

    def patch(self, old, new):
        loadable_fields = [k for k, v in self.fields.items() if k in new and not v.dump_only]
        for name in loadable_fields:
            setattr(old, name, new[name])
        current_app.session.commit()
        return old

    def delete(self, entity):
        db = current_app.session
        db.delete(entity)
        db.commit()
