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
    def __init__(self, table, **kwargs):
        self._table = table
        super().__init__(strict=False, **kwargs)

    def _validated(self, value):
        from flask.globals import current_app
        id = super()._validated(value)
        if current_app.session.query(self._table).get(id) is None:
            raise ValidationError(f'{self._table.__tablename__} `{id}` does not exist')
        return id


class BaseSchema(ma.Schema):
    known_schemas = {}

    class Meta:
        unknown = ma.RAISE
        ordered = True

    def _create_schema(self, name, fields, inner=None):
        name = f'{self.__class__.__name__.split("Schema")[0]}{name}Schema'
        if name in BaseSchema.known_schemas:
            return BaseSchema.known_schemas[name]

        if BaseSchema.Meta == getattr(self, "Meta"):
            fields["Meta"] = type("GeneratedMeta", (BaseSchema.Meta,), {"register": False})
        else:
            fields["Meta"] = type("GeneratedMeta", (BaseSchema.Meta, getattr(self, "Meta")), {"register": False})
        BaseSchema.known_schemas[name] = type(name, (BaseSchema,), fields)
        return BaseSchema.known_schemas[name]

    @classmethod
    @property
    def Creation(cls):
        """Returns the class only with load fields"""
        def create_schema(schema):
            fields = schema.load_fields
            for field in fields.values():
                if isinstance(field, ma.fields.Nested) and issubclass(field.nested, BaseSchema):
                    field.nested = create_schema(field.nested())
            return schema._create_schema("Creation", fields)
        return create_schema(cls())

    @classmethod
    @property
    def Response(cls):
        """Returns the class only with dump fields

        For all fields the required property is set to False and the missing property is reset"""
        def create_schema(schema):
            fields = schema.dump_fields
            for field in fields.values():
                field.required = False
                field.missing = missing
                if isinstance(field, ma.fields.Nested) and issubclass(field.nested, BaseSchema):
                    field.nested = create_schema(field.nested())
            return schema._create_schema("Response", fields)
        return create_schema(cls())

    @classmethod
    @property
    def Filter(cls):
        """Returns the class only with load fields, which are either Integer, String, or Boolean

        For all fields the required property is set to False, None is allowed, the missing property is reset,
        and the metadatafield "filter_description" is used as description"""
        def create_schema(schema):
            fields = {k: v for k, v in schema.load_fields.items() if isinstance(
                v, (ma.fields.Integer, ma.fields.String, ma.fields.Boolean))}
            for field in fields.values():
                field.allow_none = True
                field.required = False
                field.missing = missing
                if isinstance(field, ma.fields.Nested) and issubclass(field.nested, BaseSchema):
                    field.nested = create_schema(field.nested())
                if 'filter_description' in field.metadata:
                    field.metadata = {'description': field.metadata['filter_description']}
            return schema._create_schema("Filter", fields)
        return create_schema(cls())

    @classmethod
    @property
    def Update(cls):
        """Returns the class only with load fields

        For all fields the required property is set to False, None is allowed, and the missing property is reset"""
        def create_schema(schema):
            fields = schema.load_fields
            for field in fields.values():
                field.required = False
                field.missing = missing
                if isinstance(field, ma.fields.Nested) and issubclass(field.nested, BaseSchema):
                    field.nested = create_schema(field.nested())
            return schema._create_schema("Update", fields)
        return create_schema(cls())


class CommonSchema(BaseSchema):
    """Common fields and operations for database access"""
    id = ma.fields.Integer(dump_only=True, description='Unique ID that identifies this entity')
    date_created = ma.fields.DateTime(dump_only=True, description='Server time at which this entity was created')
    date_modified = ma.fields.DateTime(
        dump_only=True,
        allow_none=True,
        description='Server time when this entity was last modified')

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
