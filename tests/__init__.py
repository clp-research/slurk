"""Helper functions."""

from json.decoder import JSONDecodeError


def parse_error(response):
    try:
        json = response.json
    except JSONDecodeError:
        return "Unknown Error"
    if json is None:
        return "Unknown Error"
    if "errors" in json:
        return response.json["errors"]
    if "message" in json:
        return response.json["message"]
    return response.json
