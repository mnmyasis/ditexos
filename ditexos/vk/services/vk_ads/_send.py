import requests


def send(uri, payload):
    request = requests.get(uri, params=payload)
    result = request.json()
    error = result.get('error')
    if error:
        error_code = result.get('error').get('error_code')
        error_msg = result.get('error').get('error_msg')
        url = request.url
        raise ValueError(f"error_code={error_code} - error_msg={error_msg} - url={url}")
    return result
