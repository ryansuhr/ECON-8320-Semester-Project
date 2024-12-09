import streamlit as st

st.title("🎈 My new Streamlit app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.write("hello!")

import requests
import json
import pandas as pd
import os

# File path for local caching
CACHE_FILE = "bls_data.json"

def fetch_bls_data_offline():
    # Check if cached file exists
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)  # Load data from file
    else:
        # If file doesn't exist, fetch data from API
        headers = {'Content-type': 'application/json'}
        data = json.dumps({
            "seriesid": ['LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001'],
            "startyear": "2023", 
            "endyear": "2024"
        })
        response = requests.post(
            'https://api.bls.gov/publicAPI/v1/timeseries/data/',
            data=data,
            headers=headers
        )
        response.raise_for_status()  # Raise error for failed requests
        json_data = response.json()

        # Save the response locally
        with open(CACHE_FILE, "w") as f:
            json.dump(json_data, f)

        return json_data

# Use the offline-aware function to get data
json_data = fetch_bls_data_offline()

#create an empty list to store parsed data
parsed_data = []

#create a naming system for each 'period'
period_to_month = {
    'M01': 'January',
    'M02': 'February',
    'M03': 'March',
    'M04': 'April',
    'M05': 'May',
    'M06': 'June',
    'M07': 'July',
    'M08': 'August',
    'M09': 'September',
    'M10': 'October',
    'M11': 'November',
    'M12': 'December'
}

#parse the BLS data
for series in json_data['Results']['series']:
    series_id = series['seriesID']
    for item in series['data']:
        year = item['year']
        period = item['period']
        value = item['value']

        month = period_to_month.get(period, None) #implement the naming system

        parsed_data.append({
            "series_id": series_id,
            "year": year,
            "period": period,
            "month": month,
            "value": value,
        })

#create a DataFrame using the parsed data
df = pd.DataFrame(parsed_data, index=None, columns=['year', 'month', 'series_id', 'value'])

#pivot the DataFrame so that each 'series_id' becomes its own column of values 
pivot_df = df.pivot(index=['year', 'month'], columns='series_id', values='value')

# Ensure 'year' and 'month' exist in the MultiIndex
if 'year' not in pivot_df.index.names or 'month' not in pivot_df.index.names:
    raise ValueError("The pivot operation failed to include 'year' or 'month' in the index.")

#create a 'Date' column for chronological sorting
pivot_df['Date'] = pd.to_datetime(pivot_df.index.get_level_values('year').astype(str)
    + '-'
    + pivot_df.index.get_level_values('month').astype(str))

#use 'Date' to sort the Dataframe chronologically
sorted_df = pivot_df.sort_values(by=['Date'])

#reset the index ('year' and 'month' are now their own columns - removed from the multiindex)
sorted_df = sorted_df.reset_index()

#convert all data values from strings to numbers for better readability
numeric_columns = ['LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001']
for col in numeric_columns:
    if col in sorted_df.columns:
        sorted_df[col] = pd.to_numeric(sorted_df[col], errors='coerce')

#rename each 'series_id' to its actual name
sorted_df.rename(columns={
    'LNS12000000': 'Civillian Employment (thousands)',
    'LNS13000000': 'Civillian Unemployment (thousands)',
    'LNS14000000': 'Unemployment Rate (%)',
    'CES0000000001': 'Total Nonfarm Employment (thousands)'
    }, inplace=True)

#convert 'year' from a string to a number to be able to apply a filter
sorted_df['year'] = pd.to_numeric(sorted_df['year'])

#create a slider to filter the data
year_range = st.slider(
    'Filter by year',
    min_value=int(sorted_df['year'].min()),
    max_value=int(sorted_df['year'].max()),
    value=(int(sorted_df['year'].min()), int(sorted_df['year'].max()))
)

#add the slider to the Streamlit DataFrame
filtered_df = sorted_df[(sorted_df['year'] >= year_range[0]) & (sorted_df['year'] <= year_range[1])]

#convert 'year' back to a string to avoid commas in the DataFrame
filtered_df['year'] = filtered_df['year'].astype(str)

#drop the index
filtered_df.reset_index(drop=True, inplace=True)

#make the revised DataFrame a Streamlit object
st.dataframe(filtered_df)

#make a linechart
#st.line_chart(sorted_df, x='Date', y=['Civillian Employment (thousands)', 'Civillian Unemployment (thousands)', 'Total Nonfarm Employment (thousands)'])