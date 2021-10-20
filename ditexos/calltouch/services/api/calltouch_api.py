from requests import post
import pandas as pd


def send(token, site_id, start_date, end_date, page=1, limit=10):
    url = 'http://api.calltouch.ru/calls-service/RestAPI/{}/calls-diary/calls?clientApiId={}&dateFrom={}&dateTo={}&page={}&limit={}'.format(
        site_id,
        token,
        start_date,
        end_date,
        page,
        limit
    )
    result = post(url)
    result = result.json()
    df = pd.DataFrame(result['records'])
    return df, result['pageTotal']


if __name__ == '__main__':
    send()
