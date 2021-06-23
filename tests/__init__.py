def parse_error(response):
    if 'errors' in response.json:
        return response.json['errors']
    else:
        return response.json.get('message', 'Unknown Error')
