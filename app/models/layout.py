import json
import os
import urllib.request
import urllib.error

from logging import getLogger

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .common import Common


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
    if "css" not in data:
        return ""

    css = ""
    for name, properties in data["css"].items():
        css += ' ' * indent + "{} {{\n".format(name)
        for prop, value in properties.items():
            css += ' ' * indent + "    {}: {};\n".format(prop, value)
        css += ' ' * indent + "}\n\n"
    return css


def _incoming_text(content: str):
    return "incoming_text = function(data) {\n" + content + '\n}\n'


def _incoming_image(content: str):
    return "incoming_image = function(data) {\n" + content + '\n}\n'


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
        getLogger("slurk").error("invalid script for %s", trigger)
        return ""
    if trigger == "incoming-text":
        return _incoming_text(content)
    if trigger == "incoming-image":
        return _incoming_image(content)
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
    getLogger("slurk").error("unknown trigger: %s", trigger)
    return ""


def _parse_trigger(trigger, script_file):
    script = ""
    try:
        with urllib.request.urlopen(script_file) as url:
            script += _create_script(trigger, url.read().decode("utf-8")) + "\n\n\n"
    except BaseException:
        pass

    plugin_path = \
        os.path.dirname(os.path.realpath(__file__)) + \
        "/../static/plugins/" + script_file + ".js"

    try:
        with open(plugin_path) as script_content:
            script += _create_script(trigger, script_content.read()) + "\n\n\n"
    except FileNotFoundError:
        getLogger("slurk").error("Could not find script: %s", script_file)
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


class Layout(Common):
    __tablename__ = 'Layout'

    name = Column(String, nullable=False, unique=True)
    rooms = relationship("Room", backref="layout")
    tasks = relationship("Task", backref="layout")
    title = Column(String)
    subtitle = Column(String)
    html = Column(String)
    css = Column(String)
    script = Column(String)

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
        return cls.from_json_data(name, json.loads(json_data))

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
                getLogger("slurk").info("loading layout from %s", url)
                return cls.from_json_data(name, json.loads(url.read().decode()))
        except BaseException:
            pass

        layout_path = \
            os.path.dirname(os.path.realpath(__file__)) + "/../static/layouts/"

        try:
            with open(layout_path + name + ".json") as json_data:
                getLogger("slurk").info("loading layout from %s%s.json", layout_path, name)
                return cls.from_json_data(name, json.load(json_data))
        except FileNotFoundError:
            try:
                with open(layout_path + "default.json") as json_data:
                    getLogger("slurk").warn(
                        'could not find layout "%s". loaded default layout instead', name)
                    return cls.from_json_data(name, json.load(json_data))
            except FileNotFoundError:
                return None

    @classmethod
    def from_json_data(cls, name, data):
        title = _title(data)
        subtitle = _subtitle(data)
        html = _html(data)
        css = _css(data)
        script = _script(data)
        return cls(name=name, title=title, subtitle=subtitle, html=html, css=css, script=script)
