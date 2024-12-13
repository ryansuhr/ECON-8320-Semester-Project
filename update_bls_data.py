import requests
import json
import pandas as pd
import datetime
import os

#file path
CSV_FILE = ("bls_data.csv")

#function to fetch data from the BLS API
def fetch_bls_data(start_year, end_year):
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": ['LNS11000000', 'LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001'],
        "startyear": str(start_year), 
        "endyear": str(end_year)
    })
    response = requests.post(
        'https://api.bls.gov/publicAPI/v1/timeseries/data/',
        data=data,
        headers=headers
    )
    response.raise_for_status()
    return response.json()

#function to parse BLS JSON data
def parse_bls_json(json_data):
    period_to_month = {
        'M01': 'January', 'M02': 'February', 'M03': 'March', 'M04': 'April',
        'M05': 'May', 'M06': 'June', 'M07': 'July', 'M08': 'August',
        'M09': 'September', 'M10': 'October', 'M11': 'November', 'M12': 'December'
    }
    parsed_data = []
    for series in json_data['Results']['series']:
        series_id = series['seriesID']
        for item in series['data']:
            year = int(item['year'])
            period = item['period']
            value = float(item['value'])
            month = period_to_month.get(period)
            if month:  #skip non-month periods
                parsed_data.append({
                    "series_id": series_id,
                    "year": year,
                    "month": month,
                    "value": value,
                })
    return pd.DataFrame(parsed_data)

#function to fetch and append data to CSV
def fetch_and_append_data():
    #determine the start year
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        existing_years = existing_df['year'].astype(int)
        start_year = existing_years.max() + 1
    else:
        start_year = 2020

    #determine the end year for the API request
    current_year = datetime.datetime.now().year
    end_year = min(start_year + 9, current_year)

    #fetch new data
    print(f"Fetching data for years {start_year} to {end_year}...")
    json_data = fetch_bls_data(start_year, end_year)
    new_data_df = parse_bls_json(json_data)

    #append new data and remove duplicates
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        combined_df = pd.concat([existing_df, new_data_df]).drop_duplicates(subset=['series_id', 'year', 'month'])
    else:
        combined_df = new_data_df

    #save the combined data back to the CSV file
    combined_df.to_csv(CSV_FILE, index=False)
    print(f"Data updated! Added records from {start_year} to {end_year}.")

#main function to trigger the process
if __name__ == "__main__":
    fetch_and_append_data()