from requests import post
import pandas as pd
import os
from datetime import datetime


def send(token, site_id, page=1, limit=10):
    end_date = datetime.now()
    start_date = datetime(end_date.year, end_date.month, end_date.day-(end_date.day-1)).strftime("%d/%m/%Y")
    end_date = end_date.strftime("%d/%m/%Y")
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
