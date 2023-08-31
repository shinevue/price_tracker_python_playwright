import os

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def authorize_google():
    """  The file token.json stores the user's access and refresh tokens, and is
         created automatically when the authorization flow completes for the first
         time.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client-secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def append_to_sheets(creds, spreadsheet_id: str, range_name: str, value_input_option: str, values: list[list]):
    try:
        # Build the service
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        body = {
            'values': values
        }

        result = sheet.values().append(spreadsheetId=spreadsheet_id,
                                       range=range_name,
                                       valueInputOption=value_input_option,
                                       body=body).execute()

        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as err:
        print(err)


def main():
    creds = authorize_google()
    if creds:
        range_name = "A2:E2"
        values = [['hehe', 2, 'ga', 'gfda', '2023-08-02'],
                  ['hehe', 2, 'ga', 'gfda', '2023-08-02']
                  ]

        append_to_sheets(creds=creds,
                         spreadsheet_id=SPREADSHEET_ID,
                         range_name=range_name,
                         value_input_option="USER_ENTERED",
                         values=values
                         )


if __name__ == '__main__':
    main()
