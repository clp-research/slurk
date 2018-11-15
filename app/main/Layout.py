import os
import json
import urllib.request
import urllib.error

FAST_CLOSE = ["img"]


class Layout:
    @classmethod
    def from_json(cls, json_data):
        """
        Create a layout from the give JSON string
        :param json_data: the json_data to create the layout from
        :return: the Layout
        """
        return cls(json.loads(json_data))

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
            raise TypeError(f"Object of type `str` expected, however type `{type(name)}` was passed")

        print("loading layout", name)

        try:
            with urllib.request.urlopen(name) as url:
                print("loading layout from", url)
                return cls(json.loads(url.read().decode()))
        except :
            pass

        layout_path = \
            os.path.dirname(os.path.realpath(__file__)) + "/../static/layouts/" + name + ".json"

        try:
            with open(layout_path) as json_data:
                print("loading layout from", layout_path)
                return cls(json.load(json_data))
        except FileNotFoundError:
            return None

    def _node(self, node, indent=0):
        if not node:
            return ""

        if isinstance(node, str):
            return ' ' * indent + node + '\n'

        html = ""
        for entry in node:
            if isinstance(entry, str):
                html += entry
                continue

            attributes = [(k, v) for k, v in entry.items() if k != "type" and k != "content"]
            if entry["type"] == "area" or entry["type"] == "div":
                html += self._tag("div",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "span":
                html += self._tag("span",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "break" or entry["type"] == "br":
                html += self._tag("br",
                                  indent=indent,
                                  close=False)
            elif entry["type"] == "bold" or entry["type"] == "b":
                html += self._tag("b",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "emphasize" or entry["type"] == "em":
                html += self._tag("em",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "image" or entry["type"] == "img":
                html += self._tag("img",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "table":
                html += self._tag("table",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "row" or entry["type"] == "tr":
                html += self._tag("tr",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "button":
                html += self._tag("button",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "cell" or entry["type"] == "td":
                html += self._tag("td",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "plain" or entry["type"] == "pre":
                html += self._tag("pre",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
            elif entry["type"] == "audio":
                html += self._tag("audio",
                                  attributes=attributes,
                                  content=entry.get("content"),
                                  indent=indent)
        return html

    @staticmethod
    def _attribute(name, value):
        return " {}='{}'".format(name, value) if value else ""

    def _attributes(self, attributes):
        if not attributes:
            return ""

        html = ""
        for (name, value) in attributes:
            html += self._attribute(name, value)
        return html

    def _tag(self, name, attributes=None, close=True, content=None, indent=0):
        html = ' ' * indent + "<{}{}".format(name, self._attributes(attributes))
        if content:
            html += ">\n{}".format(self._node(content, indent=indent + 4))
            if close:
                html += "{}</{}".format(' ' * indent, name)
        elif close:
            if name in FAST_CLOSE:
                html += " /"
            else:
                html += "></{}".format(name)
        return html + ">\n"

    def html(self, indent=0):
        """
        Creates html from the Layout.
        :param indent: indent the html by this value
        :return: the html
        """
        if "html" not in self._data:
            return ""

        return self._node(self._data['html'], indent=indent)

    def css(self, indent=0):
        """
        Creates css from the Layout.
        :param indent: indent the css by this value
        :return: the css
        """
        if "css" not in self._data:
            return ""

        css = ""
        for name, properties in self._data["css"].items():
            css += ' ' * indent + "{} {{\n".format(name)
            for prop, value in properties.items():
                css += ' ' * indent + "    {}: {};\n".format(prop, value)
            css += ' ' * indent + "}\n\n"
        return css

    @staticmethod
    def _socket(event: str, content: str):
        return "$(document).ready(function(){socket.on('"+event+"', function(data) {"+content+"});});"

    @staticmethod
    def _submit(content: str):
        return "$('#text').keypress(function(e) {\n" \
               "    let code = e.keyCode || e.which;\n" \
               "    if (code === 13) {\n" \
               "        let text = $(e.target).val();\n" \
               "        $(e.target).val('');\n" \
               "        if (text === '') \n" \
               "            return;\n" \
               "        let current_room = self_room;\n" \
               "        let current_user = self_user;\n" \
               "        let current_timestamp = new Date().getTime();\n" \
                        + content + '\n' \
               "    }\n" \
               "});\n"

    @staticmethod
    def _history(content: str):
        return "print_history = function(history) {" \
               "    history.forEach(function(element) {\n" \
                        + content + '\n' \
               "    })\n" \
               "}\n"

    @staticmethod
    def _document_ready(content: str):
        return "$(document).ready(function(){" + content + "});"

    @staticmethod
    def _verify(content: str):
        return content.count("{") == content.count("}")

    def _create_script(self, trigger: str, content: str):
        if not self._verify(content):
            print("invalid script for", trigger)
            return ""
        if trigger == "incoming-message":
            return self._socket("message", "if (self_user.id == data.user.id) return;"+content)
        if trigger == "submit-message":
            return self._submit(content)
        if trigger == "print-history":
            return self._history(content)
        if trigger == "document-ready":
            return self._document_ready(content)
        print("unknown trigger:", trigger)
        return ""

    def script(self):
        """
        Creates a script from the Layout.
        :return: the script
        """
        if "scripts" not in self._data:
            return ""

        script = ""
        for trigger, script_file in self._data['scripts'].items():
            try:
                with urllib.request.urlopen(script_file) as url:
                    script += self._create_script(trigger, url.read().decode("utf-8")) + "\n\n\n"
            except:
                pass

            plugin_path = \
                os.path.dirname(os.path.realpath(__file__)) + "/../static/plugins/" + script_file + ".js"

            try:
                with open(plugin_path) as script_content:
                    script += self._create_script(trigger, script_content.read()) + "\n\n\n"
            except FileNotFoundError:
                print("Could not find script:", script_file)
                continue

        print(script)

        return script

    def __repr__(self):
        return json.dumps(self._data, indent=4)

    def __init__(self, data):
        self._data = data
