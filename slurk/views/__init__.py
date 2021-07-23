def register_views(api):
    from . import api as api_module, chat, login

    MODULES = (
        api_module,
        chat,
        login
    )

    for module in MODULES:
        module.register_blueprints(api)
