### IMPORT NECESSARY MODULES ###
from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pandas as pd
import requests


### 1. GATHER DATA FROM GOOGLE SHEET
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1BF_zOfOHIbg0AOtkvst9H532BspITJRKbclyt_TNzmU'
RANGE_NAME = 'Sheet1!A:F'

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    df = pd.DataFrame(values)
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    ### Iterate between row
    for index, row in df.iterrows():
      ### 2. SIGNIN TO TABLEAU SERVER
      api_ver = '3.14'
      server_url = 'https://prod-apnortheast-a.online.tableau.com/api/' + api_ver

      ### AUTHENTHICATE ###
      url = server_url + '/auth/signin'
      headers = {
                  "Content-Type": "application/json",
                  "Accept"      : "application/json"
                }
      payload = {
                  "credentials": {
                                    "personalAccessTokenName"   : row['PAT Name'],
                                    "personalAccessTokenSecret" : row['PAT Secret'],
                                    "site": {
                                              "contentUrl": "skctableau"
                                            }
                                  }
                }

      res = requests.post(url, headers=headers, json = payload)
      res = res.json()
      token = res['credentials']['token']
      site_id = res['credentials']['site']['id']
      ### 3. GET DASHBOARD IMAGE
      url = server_url +  '/sites/' + site_id + '/views/' + row['Dashboard ID'] + '/image' + '?maxAge=5'+'&resolution=high'
      if row['FilterField'] != '':
        url = url + '&vf_' + row['FilterField'] + '=' + row['FilterValue']
      headers = {
                  "Content-Type"  : "application/json",
                  "Accept"        : "application/json",
                  "X-Tableau-Auth": token
                }
      res = requests.get(url, headers=headers, json = {})
      ### 4. SEND TO LINE NOTIFY
      Headers = {
        'Authorization':'Bearer ' + row['Line Token']
      }
      Message = {
        'message':'สวัสดีครับ'
      }
      files = {'imageFile':res.content}

      response = requests.post('https://notify-api.line.me/api/notify',
                              data=Message,
                              headers=Headers,
                              files=files)
except HttpError as err:
    print(err)