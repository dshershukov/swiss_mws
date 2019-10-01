import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials as SAC
from google_formatting import get_data_request, get_format_request, get_pair_position
CREDENTIALS_FILE = 'google_token.json'


credentials = SAC.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                              'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
#doc_id ='1pdeBOVo3SFBAXPw6wcPfK3bn_yQfNcuNBFVpwOpdfGg'


def create_new_doc(name, rounds=1, rows=1000, columns=25):
    sheets = []
    for r in range(rounds):
        sheets.append(
        {'properties': {'sheetType': 'GRID',
                        'sheetId': r,
                        'title': 'Round_{}'.format(r-1),
                        'gridProperties': {'rowCount': rows, 'columnCount': columns}}})

    try:
        spreadsheet = service.spreadsheets().create(body={
            'properties': {'title': name, 'locale': 'ru_RU'},
            'sheets': sheets
        }).execute()
    except Exception as e:
        print('Creation failed\n' + str(e))
        return ''
    return spreadsheet['spreadsheetId']


def add_sheet(spreadsheetId, sheet_name, color_left, color_right):
    # To add a sheet to the existing document
    # did not try this yet, so now we just have to make the number of sheets at the doc creation
    raise NotImplementedError


class GoogleAPI:
    def __init__(self, spreadsheet_id=None, num_areas=2,
                 name="", collaborators=None, rounds=1, **kwargs):
        self.num_areas = num_areas
        if spreadsheet_id is not None:
            self._spreadsheet_id = spreadsheet_id
        else:
            self._spreadsheet_id = create_new_doc(name, rounds=1, **kwargs)
        if collaborators is not None:
            self.share(collaborators)
        for r in range(rounds):
            self.fill_heading(r)

    @property
    def spreadsheet_id(self):
        return self._spreadsheet_id

    @property
    def SpreadsheetURL(self):
        return 'https://docs.google.com/spreadsheets/d/{}/edit#gid=0'.format(self._spreadsheet_id)

    def write(self, pairs, round_num):
        pairs_in_area = int(len(pairs)/self.num_areas)
        # it is rounded, so the last area may get more pairs.
        # 15 pairs, 2 areas = 7+8
        # problem may be: 15 pairs, 4 areas: 3+3+3+6
        # todo: fix to make pair numbers more even (not necessary for 2 areas)
        #pairs_in_areas = [pairs_in_area]*(self.num_areas-1) + [len(pairs) - pairs_in_area*(self.num_areas-1)]
        area_pairs = [pairs[pairs_in_area*i: pairs_in_area*(i+1)] for i in range(self.num_areas-1)]
        area_pairs += [pairs[pairs_in_area*(self.num_areas-1):]]

        for i, area in enumerate(area_pairs):
            position = get_pair_position(round_num, i, len(area))
            pair_data = [pair[0].to_list() + pair[1].to_list()[::-1] for pair in area]
            data_request = {
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        {"range": position,
                         "majorDimension": "ROWS",
                         # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
                         "values": pair_data}
            ]}
            service.spreadsheets().values().batchUpdate(spreadsheetId=self._spreadsheet_id,
                                                                  body=data_request).execute()
        return self.SpreadsheetURL

    def read(self, round_num):
        data = []
        for area in range(self.num_areas):
            read_range = get_pair_position(round_num, area, 1000)
            print(read_range)
            response = service.spreadsheets().values().get(spreadsheetId=self._spreadsheet_id,
                                                           range=read_range).execute()
            # response['values'] = [[fighter1, hp1, result1, result2, hp2, fighter2],[...]]
            # we format it in the api standard ((fighter1, result1), (figther2, result2))
            results = [((fight[0], fight[2]), (fight[5], fight[3])) for fight in response['values']]
            data += results
        return data

    def share(self, collaborators):
        drive_service = apiclient.discovery.build('drive', 'v3', http=httpAuth)
        for email in collaborators:
            drive_service.permissions().create(
                fileId=self._spreadsheet_id,
                body={'type': 'user', 'role': 'writer', 'emailAddress': email},
                fields='id'
            ).execute()

    def fill_heading(self, sheetId, rows=1000):
        request = get_format_request(sheetId, rows)
        # Execute the request
        try:
            service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                     body={"requests": request}).execute()
        except Exception as e:
            print('Failed to format the page {}\n'.format(sheetId) + str(e))

        # Data request - fill the static data
        data_request = get_data_request(sheetId)
        try:
            service.spreadsheets().values().batchUpdate(spreadsheetId=self._spreadsheet_id,
                                                              body=data_request).execute()
        except Exception as e:
            print('Failed to put the table header {}\n'.format(sheetId) + str(e))
        return
