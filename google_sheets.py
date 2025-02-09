import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_google_sheets_data():
    """
    Fetch data from Google Sheets using service account
    """
    try:
        # Google Sheets setup
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SPREADSHEET_ID = '19emAWfw4K7EmKceauFVq7zzpOXsNV03iCneadthpnLs'
        RANGE_NAME = 'Sheet1!A:B'  # Specify the range for Item Name and Price columns

        @st.cache_resource
        def authenticate_google_sheets():
            try:
                # Use secrets from .streamlit/secrets.toml
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=SCOPES
                )
                service = build('sheets', 'v4', credentials=credentials)
                return service
            except Exception as auth_error:
                st.error(f"Authentication error: {str(auth_error)}")
                return None

        service = authenticate_google_sheets()
        if not service:
            st.error("Failed to authenticate with Google Sheets")
            return pd.DataFrame(columns=['Item Name', 'Price'])

        try:
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()

            values = result.get('values', [])
            if not values:
                st.error('No data found in Google Sheet')
                return pd.DataFrame(columns=['Item Name', 'Price'])

            # Create DataFrame from the values
            if len(values) > 1:  # Check if we have data beyond headers
                # Make sure we have exactly two columns
                df = pd.DataFrame(values[1:], columns=['Item Name', 'Price'])

                # Clean the data
                df['Item Name'] = df['Item Name'].str.strip()
                df['Price'] = pd.to_numeric(
                    df['Price'].astype(str)
                        .str.replace('₹', '')
                        .str.replace(',', '')
                        .str.strip(), 
                    errors='coerce'
                )

                # Drop any rows with NaN values
                df = df.dropna()

                # Log success
                st.write(f"Successfully loaded {len(df)} items from Google Sheets")
                return df
            else:
                st.error('No data rows found in Google Sheet')
                return pd.DataFrame(columns=['Item Name', 'Price'])

        except Exception as sheet_error:
            st.error(f"Error reading sheet: {str(sheet_error)}")
            return pd.DataFrame(columns=['Item Name', 'Price'])

    except Exception as e:
        st.error(f"Error in Google Sheets setup: {str(e)}")
        return pd.DataFrame(columns=['Item Name', 'Price'])