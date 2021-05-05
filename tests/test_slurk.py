# import os
# import tempfile

# import pytest

# from slurk import create_app
# from slurk.database import create_session


# @pytest.fixture(autouse=True)
# def environment():
#     old_environ = dict(os.environ)
#     os.environ.clear()
#     database_file = tempfile.NamedTemporaryFile()
#     os.environ.update({
#         'SECRET_KEY': 'test',
#         'DATABASE': f'sqlite:///{database_file.name}.db'
#     })

#     yield

#     os.environ.clear()
#     os.environ.update(old_environ)

# @pytest.fixture
# def token(app):
#     from slurk.models import Token, Permissions, Room, Layout
    
#     db = app.session
#     print(db.query(Layout).all())
#     token = Token(
#         id='00000000-0000-0000-0000-000000000000',
#         permissions=Permissions(),
#         room=Room(
#             name="test_room",
#             label="Test Room",
#             layout=Layout.from_json_file("default"),
#             static=True))
#     db.add(token)
#     db.commit()


# @pytest.fixture
# def app():
#     return create_app({'TESTING': True} | os.environ)


# @pytest.fixture
# def client(app):
#     return app.test_client()


# @pytest.fixture
# def runner(app):
#     return app.test_cli_runner()


# def test_config():
#     assert not create_app().testing
#     assert create_app({'TESTING': True} | os.environ).testing


# def test_login(app, client, token):
#     pass
    


# def test_(app):
#     pass
