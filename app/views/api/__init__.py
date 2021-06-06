import marshmallow as ma

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
        super().__init__(strict=True, **kwargs)

    def _validated(self, value):
        from flask.globals import current_app
        # id = super()._validated(value)
        id = value
        self.error_messages['foreign_key'] = f'{self._table.__tablename__} `{id}` does not exist'
        if current_app.session.query(self._table).get(id) is None:
            raise self.make_error('foreign_key')
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

    def put(self, old, new):
        loadable_fields = [k for k, v in self.fields.items() if not v.dump_only]
        for name in loadable_fields:
            setattr(old, name, getattr(new, name, None))
        return old

    def patch(self, old, new):
        loadable_fields = [
            k for k, v in self.fields.items() if getattr(new, k, None) and not v.dump_only
        ]
        for name in loadable_fields:
            setattr(old, name, getattr(new, name))
        return old
