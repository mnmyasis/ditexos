from requests import post
import pandas as pd
import os


def send():
    token = os.environ.get('CALLTOUCH_TOKEN')
    site_id = '13480'
    url = 'http://api.calltouch.ru/calls-service/RestAPI/{}/calls-diary/calls?clientApiId={}&dateFrom=27/05/2021&dateTo=28/05/2021&page=1&limit=10'.format(
        site_id, token)
    result = post(url)
    result = result.json()
    df = pd.DataFrame(result['records'])
    print(df.columns.to_list())
    print(df)
    return df


if __name__ == '__main__':
    send()
