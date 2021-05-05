from flask import current_app
from flask.cli import with_appcontext
import click

from ..models import Token, Permissions, Room, Layout


def add_layout_from_json(path):
    db = current_app.session
    layout = Layout.from_json_file(path)
    db.add(layout)
    db.commit()
    return layout.id


@click.command('add-layout-from-json')
@click.argument('path')
@with_appcontext
def add_layout_from_json_command(path):
    layout = add_layout_from_json(path)
    click.echo(f'Layout added: {token}')
