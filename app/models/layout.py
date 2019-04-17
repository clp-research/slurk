from flask_login import current_user

import json
import os
import urllib.request
import urllib.error

from . import Base
from .. import db, socketio


def _title(data):
    if "title" not in data:
        return ""

    return data['title']


def _subtitle(data):
    if "subtitle" not in data:
        return ""

    return data['subtitle']


def _node(node, indent=0):
    if not node:
        return ""

    if isinstance(node, str):
        return ' ' * indent + node + '\n'

    html = ""
    for entry in node:
        if isinstance(entry, str):
            html += entry
            continue
        ty = entry.get("layout-type")
        if not ty:
            continue
        if ty == "br":
            html += _tag(ty, indent=indent, close=False)
        else:
            attributes = [(k, v) for k, v in entry.items()
                          if k != "layout-type" and k != "layout-content"]
            html += _tag(ty, attributes=attributes, content=entry.get("layout-content"), indent=indent)
    return html


def _attribute(name, value):
    return " {}='{}'".format(name, value) if value else ""


def _attributes(attributes):
    if not attributes:
        return ""

    html = ""
    for (name, value) in attributes:
        html += _attribute(name, value)
    return html


def _tag(name, attributes=None, close=True, content=None, indent=0):
    html = ' ' * indent + \
           "<{}{}".format(name, _attributes(attributes))
    if content:
        html += ">\n{}".format(_node(content, indent=indent + 4))
        if close:
            html += "{}</{}".format(' ' * indent, name)
    elif close:
        if name in ['img']:
            html += " /"
        else:
            html += "></{}".format(name)
    return html + ">\n"


def _html(data, indent=0):
    if "html" not in data:
        return ""

    return _node(data['html'], indent=indent)


def _css(data, indent=0):
    """
    Creates css from the Layout.
    :param indent: indent the css by this value
    :return: the css
    """
    if "css" not in data:
        return ""

    css = ""
    for name, properties in data["css"].items():
        css += ' ' * indent + "{} {{\n".format(name)
        for prop, value in properties.items():
            css += ' ' * indent + "    {}: {};\n".format(prop, value)
        css += ' ' * indent + "}\n\n"
    return css


def _incoming_message(content: str):
    return "incoming_message = function(data) {\n" + content + '\n}\n'


def _submit(content: str):
    return "keypress = function(current_room, current_user, current_timestamp, text) {" + content + "}"


def _history(content: str):
    return "print_history = function(history) {\n" \
           "    history.forEach(function(element) {\n" \
           + content + '\n' \
                       "    })\n" \
                       "}\n"


def _typing_users(content: str):
    return "update_typing = function(users) {\n" + content + '\n}\n'


def _document_ready(content: str):
    return "$(document).ready(function(){" + content + "});"


def _verify(content: str):
    return content.count("{") == content.count("}")


def _create_script(trigger: str, content: str):
    if not _verify(content):
        print("invalid script for", trigger)
        return ""
    if trigger == "incoming-message":
        return _incoming_message(content)
    if trigger == "submit-message":
        return _submit(content)
    if trigger == "print-history":
        return _history(content)
    if trigger == "document-ready":
        return _document_ready(content)
    if trigger == "typing-users":
        return _typing_users(content)
    if trigger == "plain":
        return content
    print("unknown trigger:", trigger)
    return ""


def _parse_trigger(trigger, script_file):
    script = ""
    try:
        with urllib.request.urlopen(script_file) as url:
            script += _create_script(trigger, url.read().decode("utf-8")) + "\n\n\n"
    except:
        pass

    plugin_path = \
        os.path.dirname(os.path.realpath(__file__)) + \
        "/../static/plugins/" + script_file + ".js"

    try:
        with open(plugin_path) as script_content:
            script += _create_script(trigger, script_content.read()) + "\n\n\n"
    except FileNotFoundError:
        print("Could not find script:", script_file)
    return script


def _script(data):
    if "scripts" not in data:
        return ""

    script = ""
    for trigger, script_file in data['scripts'].items():
        if isinstance(script_file, str):
            script += _parse_trigger(trigger, script_file)
        else:
            for file in iter(script_file):
                script += _parse_trigger(trigger, file)

    return script


class Layout(Base):
    __tablename__ = 'Layout'

    name = db.Column(db.String, nullable=False, unique=True)
    rooms = db.relationship("Room", backref="layout")
    title = db.Column(db.String)
    subtitle = db.Column(db.String)
    html = db.Column(db.String)
    css = db.Column(db.String)
    script = db.Column(db.String)

    def as_dict(self):
        return dict({
            'name': self.name,
            'title': self.title,
            'subtitle': self.subtitle,
            'html': self.html,
            'css': self.css,
            'script': self.script,
        }, **super(Layout, self).as_dict())

    @classmethod
    def from_json(cls, name, json_data):
        """
        Create a layout from the give JSON string
        :param name: the name of the layout
        :param json_data: the json_data to create the layout from
        :return: the Layout
        """
        return cls._from_json_data(name, json.loads(json_data))

    @classmethod
    def from_json_file(cls, name: str):
        """
        Create a layout from the give file name. The file must be either a URL or
        lie in `app/static/layouts` and the extension. For the latter, the file
        extension must be omitted.

        Example: ``Layout.from_json_file("Meetup")``
        :param name: the url or the file name
        :return: the Layout
        """
        if not name:
            return None
        if not isinstance(name, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(name)}` was passed")

        try:
            with urllib.request.urlopen(name) as url:
                print("loading layout from", url)
                return cls._from_json_data(name, json.loads(url.read().decode()))
        except:
            pass

        layout_path = \
            os.path.dirname(os.path.realpath(__file__)) + "/../static/layouts/"

        try:
            with open(layout_path + name + ".json") as json_data:
                print("loading layout from", layout_path + name + ".json")
                return cls._from_json_data(name, json.load(json_data))
        except FileNotFoundError:
            try:
                with open(layout_path + "default.json") as json_data:
                    print(
                        f"could not find layout \"{name}\". loaded default layout instead")
                    return cls._from_json_data(name, json.load(json_data))
            except FileNotFoundError:
                return None

    @classmethod
    def _from_json_data(cls, name, data):
        title = _title(data)
        subtitle = _subtitle(data)
        html = _html(data)
        css = _css(data)
        script = _script(data)
        return cls(name=name, title=title, subtitle=subtitle, html=html, css=css, script=script)


@socketio.on('get_layout')
def _get_layout(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.layout_query:
        return False, "insufficient rights"
    layout = Layout.query.get(id)
    if layout:
        return True, layout.as_dict()
    else:
        return False, "layout does not exist"
