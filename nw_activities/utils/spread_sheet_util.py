from typing import List

from gspread import Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials


class GSpreadUtility:
    _credentials = None

    def __init__(self):
        from django.conf import settings

        gspread_conf = settings.GSPREAD_CONFIGURATION
        config_file_path = gspread_conf.get("config_file_path")
        scopes = gspread_conf.get("scopes")
        self.authenticate(config_file_path, scopes)

    def authenticate(self, config_file_path, scopes):
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(
            config_file_path, scopes,
        )

    def authorize(self):
        import gspread
        gspread_handler = gspread.authorize(self._credentials)
        return gspread_handler

    def get_sheet_obj(self, spreadsheet_id):
        try:
            gspread_handler = self.authorize()
            sheet_obj = gspread_handler.open_by_key(spreadsheet_id)
            return sheet_obj
        except Exception as e:
            raise e


class GSpreadPopulateUtils(GSpreadUtility):
    def __init__(self, spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id
        super(GSpreadPopulateUtils, self).__init__()

    def get_spread_sheet_data(self, sheet_name) -> List[List[str]]:
        import gspread

        try:
            gc = gspread.authorize(self._credentials)
            try:
                sh = gc.open_by_key(self.spreadsheet_id)
            except Exception as e:
                raise e

            worksheets = sh.worksheets()
            for worksheet in worksheets:
                if worksheet.title == sheet_name:
                    return worksheet.get_all_values()

        except Exception as e:
            raise e

    def get_sheet_data_using_spread_sheet_name(
            self, spread_sheet_name: str, sub_sheet_name: str,
    ) -> List[List[str]]:
        import gspread
        gc = gspread.authorize(self._credentials)
        wks = gc.open(spread_sheet_name).worksheet(sub_sheet_name)
        list_of_lists = wks.get_all_values()
        return list_of_lists

    def get_spread_sheet_obj(self) -> Spreadsheet:

        import gspread

        gc = gspread.authorize(self._credentials)
        try:
            sheet_obj = gc.open_by_key(self.spreadsheet_id)
        except Exception as e:
            raise e

        return sheet_obj

    def add_data_to_spread_sheet(self, data, sheet_name):
        import gspread

        try:
            gc = gspread.authorize(self._credentials)
            try:
                sh = gc.open_by_key(self.spreadsheet_id)
            except Exception as e:
                raise e

            worksheet_obj = None

            worksheets = sh.worksheets()
            for worksheet in worksheets:
                if worksheet.title == sheet_name:
                    worksheet_obj = worksheet

            if not worksheet_obj:
                worksheet_obj = sh.add_worksheet(
                    rows=len(data), cols=20, title=sheet_name,
                )

            worksheet_obj.insert_rows(data)

        except Exception as e:
            raise e

    def update_data_to_spread_sheet(self, data, sheet_name):
        import gspread
        from gspread.models import Cell

        try:
            gc = gspread.authorize(self._credentials)
            try:
                sh = gc.open_by_key(self.spreadsheet_id)
            except Exception as e:
                raise e

            worksheet_obj = None

            worksheets = sh.worksheets()
            for worksheet in worksheets:
                if worksheet.title == sheet_name:
                    worksheet_obj = worksheet

            if not worksheet_obj:
                worksheet_obj = sh.add_worksheet(
                    rows=len(data), cols=20, title=sheet_name,
                )

            cells = [Cell(row=row[0], col=row[1], value=row[2]) for row in data]
            if cells:
                worksheet_obj.update_cells(cells)

        except Exception as e:
            raise e

    def get_sheet_names(self) -> List[str]:
        import gspread

        sheet_names = []
        try:
            gc = gspread.authorize(self._credentials)
            try:
                sh = gc.open_by_key(self.spreadsheet_id)
            except Exception as e:
                raise e

            worksheets = sh.worksheets()
            for worksheet in worksheets:
                sheet_names.append(worksheet.title)
        except Exception as e:
            raise e

        return sheet_names
