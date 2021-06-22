from copy import deepcopy
from functools import wraps
from flask.globals import current_app, request
from uuid import UUID
from requests import Response
from json import JSONDecodeError
from werkzeug.exceptions import UnsupportedMediaType

import flask_smorest
import http


class ErrorHandlerMixin(flask_smorest.ErrorHandlerMixin):
    def handle_http_exception(self, error):
        if error:
            if hasattr(error, 'data'):
                error.data['message'] = error.description
            else:
                setattr(error, 'data', dict(message=error.description))
        return super().handle_http_exception(error)


class ResponseReferencesPlugin(flask_smorest.spec.plugins.ResponseReferencesPlugin):
    def _available_responses(self):
        specs = super()._available_responses()
        del specs['NOT_MODIFIED']['schema']
        return specs


class Blueprint(flask_smorest.Blueprint):
    def register_blueprint(self, blueprint, **options):
        url_prefix = self.url_prefix + blueprint.url_prefix + options.get('url_prefix', '')
        super().register_blueprint(blueprint, **options, url_prefix=url_prefix)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prepare_doc_cbks.append(self._prepare_auth_doc)
        self._prepare_doc_cbks.append(self._prepare_404_doc)

    def arguments(self, schema, *, location='json', **kwargs):
        super_arguments = super().arguments(schema, location=location, **kwargs)

        def decorator(func):
            func = super_arguments(func)

            @wraps(func)
            def wrapper(*f_args, **f_kwargs):
                if location == 'json' \
                        and (len(request.data) > 0 or len(request.form) > 0 or len(request.files) > 0) \
                        and request.content_type != "application/json":
                    abort(UnsupportedMediaType)
                return func(*f_args, **f_kwargs)
            wrapper._apidoc['arguments']['responses'][415] = http.HTTPStatus(415).name
            return wrapper
        return decorator

    @staticmethod
    def login_required(func):
        from app.views.api.auth import auth
        from flask.globals import current_app
        if not current_app.config['DEBUG']:
            func = auth.login_required(func)
        getattr(func, "_apidoc", {})["auth"] = True
        return func

    @staticmethod
    def _prepare_auth_doc(doc, doc_info, **kwargs):
        if doc_info.get("auth", False):
            doc.setdefault("responses", {})["401"] = http.HTTPStatus(401).name
            doc["security"] = [{"TokenAuthentication": []}]
        return doc

    @staticmethod
    def _prepare_404_doc(doc, doc_info, **kwargs):
        if doc_info.get("validate", False):
            doc.setdefault("responses", {})["404"] = http.HTTPStatus(404).name
        return doc

    def route(self, rule, *, parameters=None, **options):
        # Trim trailing `/`
        if rule.endswith('/'):
            rule = rule[:-1]
        return super().route(rule, parameters=parameters, **options)

    def query(self, parameter, schema, check_etag=True):
        """
        Used as decorator for getting an entity by id.

        Searches for "`parameter`_id" and passes the entity as "`parameter`" to the
        decorated function.
        """
        cls = schema.Meta.model

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                parameter_id = f'{parameter}_id'
                id = kwargs.pop(parameter_id)
                if isinstance(id, UUID):
                    id = str(id)
                entry = current_app.session.query(cls).get(id)
                if not entry:
                    flask_smorest.abort(http.HTTPStatus.NOT_FOUND, errors=dict(query={
                        parameter_id: f'{cls.__tablename__} `{id}` does not exist'
                    }
                    ))
                if check_etag and request.method in self.METHODS_NEEDING_CHECK_ETAG:
                    self.check_etag(entry, schema)

                kwargs[parameter] = entry
                return func(*args, **kwargs)

            wrapper._apidoc = deepcopy(getattr(wrapper, '_apidoc', {}))
            wrapper._apidoc['validate'] = True
            return wrapper
        return decorator


class Api(flask_smorest.Api, ErrorHandlerMixin):
    def register_blueprint(self, blp, **options):
        if isinstance(blp, Blueprint):
            return super().register_blueprint(blp, **options)
        else:
            return self._app.register_blueprint(blp, **options)

    def init_app(self, app, *, spec_kwargs=None):
        # Don't show default error in OpenAPI
        self.DEFAULT_ERROR_RESPONSE_NAME = None
        # Mark `errors` in error scheme as nullable
        self.ERROR_SCHEMA.errors.allow_none = True

        spec_kwargs = spec_kwargs or {}
        spec_kwargs['response_plugin'] = ResponseReferencesPlugin(self.ERROR_SCHEMA)
        super().init_app(app, spec_kwargs=spec_kwargs)

        # Add Token Authentication to OpenAPI
        self.spec.components.security_scheme(
            "TokenAuthentication", dict(type='http', scheme='bearer')
        )


api = Api()


def init_app(app):
    from app.views import register_views

    api.init_app(app)
    register_views(api)


def abort(ex, *, json={}, query={}):
    from flask import abort, make_response
    from werkzeug.http import HTTP_STATUS_CODES
    from werkzeug.exceptions import default_exceptions

    if isinstance(ex, Response):
        try:
            if 'message' in ex.json() \
                    and len(json) == 0 \
                    and ex.json()['message'] is not None \
                    and ex.json()['message'] != '':
                json = ex.json()['messsage']
        except JSONDecodeError:
            pass
        ex = default_exceptions[ex.status_code]

    payload = dict(
        code=ex.code,
        message=ex.description,
        status=HTTP_STATUS_CODES.get(ex.code, "Unknown Error"))
    if len(json) > 0:
        payload.setdefault('errors', {})['json'] = json
    if len(query) > 0:
        payload.setdefault('errors', {})['query'] = query

    abort(make_response(payload, ex.code))
