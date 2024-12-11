import requests
import json
import pandas as pd
import datetime
import os

# File paths
CACHE_FILE = "bls_data.json"
CSV_FILE = "bls_data.csv"

# Current year
current_year = datetime.datetime.now().year

# Function to fetch data from the BLS API
def fetch_bls_data():
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": ['LNS11000000', 'LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001'],
        "startyear": "2015", 
        "endyear": str(current_year)
    })
    response = requests.post(
        'https://api.bls.gov/publicAPI/v1/timeseries/data/',
        data=data,
        headers=headers
    )
    response.raise_for_status()
    return response.json()

# Function to parse BLS JSON data
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
            year = item['year']
            period = item['period']
            value = item['value']
            month = period_to_month.get(period)
            if month:  # Skip non-month periods
                parsed_data.append({
                    "series_id": series_id,
                    "year": year,
                    "month": month,
                    "value": value,
                })
    return pd.DataFrame(parsed_data)

def main():
    try:
        # Fetch and parse data
        json_data = fetch_bls_data()
        df = parse_bls_json(json_data)
        
        # Save the cache with timestamp
        cache = {"last_updated": datetime.datetime.now().strftime("%Y-%m-%d"), "data": json_data}
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)

        # Save to CSV
        df.to_csv(CSV_FILE, index=False)
        print("Data updated successfully!")
    except Exception as e:
        print(f"Failed to update data: {e}")

if __name__ == "__main__":
    main()