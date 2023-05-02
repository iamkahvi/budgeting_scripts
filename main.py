from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pandas as pd
from datetime import datetime
from googleapiclient.errors import HttpError
import os
from typing import List, Tuple
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

# ... (Your existing authentication code)


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Read all CSV files from the "input csvs" folder
        input_folder = "input_csvs"
        csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

        # Process each CSV file
        for csv_file in csv_files:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(os.path.join(input_folder, csv_file))

            # Parse the date column and organize the data
            date_col = df.columns[0]
            df[date_col] = pd.to_datetime(df[date_col], format="%m/%d/%Y")
            df = df.sort_values(by=date_col)

            # Create a new Google Sheet with the name of the CSV file (excluding the .csv extension)
            sheet_name = clean_sheet_name(os.path.splitext(csv_file)[0])
            spreadsheet_id = create_google_sheet(service, sheet_name)

            # Write the DataFrame to the Google Sheet
            write_to_google_sheet(service, spreadsheet_id, sheet_name, df)

    except HttpError as err:
        print(err)


import re


def clean_sheet_name(sheet_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", sheet_name)


# Add the following function to create a new Google Sheet
def create_google_sheet(service: Resource, title: str) -> str:
    sheet_metadata = {"properties": {"title": title}}
    sheet = service.spreadsheets().create(body=sheet_metadata).execute()
    print(
        f'Created spreadsheet with title: {sheet.get("properties", {}).get("title", "Untitled")}'
    )
    return sheet.get("spreadsheetId")


def write_to_google_sheet(
    service: Resource, spreadsheet_id: str, sheet_name: str, df: pd.DataFrame
) -> None:
    # Wrap the sheet name in single quotes
    cell_range = f"A1:Z"

    # Convert datetime values to string format and replace NaN values with empty strings
    df = df.applymap(
        lambda x: x.strftime("%Y-%m-%d")
        if isinstance(x, pd.Timestamp)
        else ("" if pd.isna(x) else x)
    )

    body = {
        "range": cell_range,
        "majorDimension": "ROWS",
        "values": [df.columns.tolist()] + df.values.tolist(),
    }

    try:
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=cell_range,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )
        print(f'{result.get("updatedCells")} cells updated in Google Sheet.')
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
