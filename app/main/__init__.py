from flask import Blueprint
import sys

main = Blueprint('main', __name__)

print("server started")
sys.stdout.flush()

from . import routes, events
