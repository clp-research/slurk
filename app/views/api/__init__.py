import marshmallow as ma
from flask.globals import current_app
from marshmallow.exceptions import ValidationError
from marshmallow.utils import missing


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


class BaseSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE
        ordered = True

    def _create_schema(self, name, fields):
        base_name = self.__class__.__name__.split('Schema')[0]
        fields["Meta"] = type("GeneratedMeta", (BaseSchema.Meta, getattr(self, "Meta", object)), {"register": False})
        return type(f'{base_name}{name}Schema', (BaseSchema,), fields)

    @property
    def creation_schema(self):
        return self._create_schema("Creation", self.load_fields)

    @property
    def response_schema(self):
        fields = self.dump_fields
        for field in fields.values():
            field.required = False
            field.missing = missing
        return self._create_schema("Response", fields)

    @property
    def query_schema(self):
        fields = {k: v for k, v in self.load_fields.items() if isinstance(
            v, (ma.fields.Integer, ma.fields.String, ma.fields.Boolean))}
        for field in fields.values():
            field.allow_none = True
            field.required = False
            field.missing = missing
            if 'filter_description' in field.metadata:
                field.metadata = {'description': field.metadata['filter_description']}
        return self._create_schema("Query", fields)

    @property
    def update_schema(self):
        fields = self.load_fields
        for field in fields.values():
            field.allow_none = True
            field.required = False
            field.missing = missing
        return self._create_schema("Update", fields)

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
        for field in self.load_fields.keys():
            setattr(old, field, getattr(entity, field, None))
        current_app.session.commit()
        return old

    def patch(self, old, new):
        for field in self.load_fields.keys():
            if field in new:
                setattr(old, field, new[field])
        current_app.session.commit()
        return old

    def delete(self, entity):
        db = current_app.session
        db.delete(entity)
        db.commit()


class CommonSchema(BaseSchema):
    id = ma.fields.Integer(dump_only=True, description='Unique ID that identifies this entity')
    date_created = ma.fields.DateTime(dump_only=True, description='Server time at which this entity was created')
    date_modified = ma.fields.DateTime(dump_only=True, description='Server time when this entity was last modified')
