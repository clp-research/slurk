from flask import Blueprint

main = Blueprint('main', __name__)

print("server started")

from . import routes, events
