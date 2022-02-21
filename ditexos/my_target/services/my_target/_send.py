import requests

host = 'target.my.com'


def send_get(path, params=None, headers=None):
    url = f"https://{host}{path}"
    response = requests.get(url, params=params, headers=headers)
    result = response.json()
    error = result.get('error')
    if error:
        error_code = error
        error_msg = result.get('error_description')
        raise ValueError(f"error_code={error_code} - error_msg={error_msg} - url={response.url}")
    return result


def send_post(path, payloads):
    url = f"https://{host}{path}"
    response = requests.post(url, data=payloads)
    result = response.json()
    error = result.get('error')
    if error:
        error_code = error
        error_msg = result.get('error_description')
        raise ValueError(f"error_code={error_code} - error_msg={error_msg} - url={url}")
    return result
