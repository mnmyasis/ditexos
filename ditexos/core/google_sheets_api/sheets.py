from typing import Dict

from core import SpreadSheet


class Sheets(SpreadSheet):
    RESULT = Dict[str, list]

    def get_url(self) -> str:
        return self.URL.format(spead_sheet_id=self.spreadsheet_id)

    def get_headers(self) -> Dict[str, str]:
        return {
            'authorization': f'Bearer {self.access_token}'
        }

    def processing_require(self) -> None:
        result = self.REQUIRE.json()
        sheet_ids = []
        sheet_titles = []
        for sheet in result['sheets']:
            sheet_ids.append(sheet['properties']['sheetId'])
            sheet_titles.append(sheet['properties']['title'])
        self.RESULT = {
            'ids': sheet_ids,
            'titles': sheet_titles
        }

    def orchestrator(self) -> None:
        self._request()
        self.processing_require()
        print(self.RESULT)


if __name__ == '__main__':
    token = 'ya29.A0ARrdaM9Vre0NzRjFa-TnvKgn7cQrv5SwBLUxjQ1G9wdKA9fvIULJb_h2JBykObIE3xZmwZ8Cxa2Q53rdXlfUG5HdGT8GWxzzohAoXueGOw-pjulpUojCK2R-NiSPwHhAIh9lIbo7ToH_p-u9TXk0OgVf_KG9'
    spreadsheet_id = '1xwbxeLmE8O7wcK5ySa2wbAZrgbpd62F4I6FIwu8PLgc'
    sheets = Sheets(spreadsheet_id=spreadsheet_id, access_token=token)
    sheets.orchestrator()
