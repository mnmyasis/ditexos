import requests


class SpreadSheet:
    GOOD_STATUS_CODE = 200
    URL = 'https://sheets.googleapis.com/v4/spreadsheets/{spead_sheet_id}/'
    REQUIRE = None

    def __init__(self,
                 spreadsheet_id: str,
                 access_token: str) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.access_token = access_token

    def get_url(self):
        raise NotImplementedError

    def get_headers(self):
        raise NotImplementedError

    def _request(self) -> None:
        url = self.get_url()
        headers = self.get_headers()
        require = requests.get(url, headers=headers)
        if require.status_code != self.GOOD_STATUS_CODE:
            require.raise_for_status()
        self.REQUIRE = require
