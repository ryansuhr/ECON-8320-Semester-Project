import streamlit as st

#enable wide mode
st.set_page_config(layout="wide")

st.title("🎈 My new Streamlit app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.write("hello!")

import pandas as pd
import requests
import json
import pandas as pd
import datetime
import os

#get the current year
current_year = datetime.datetime.now().year

#create file paths for local caching
CACHE_FILE = "bls_data.json"
CSV_FILE = "bls_data.csv"

#define a BLS data-fetching function
def fetch_bls_data_offline():
    #check if CSV exists
    if os.path.exists(CSV_FILE):
        #st.write("Loading data from CSV file.")
        return pd.read_csv(CSV_FILE)

    #check if JSON cache exists
    elif os.path.exists(CACHE_FILE):
        #st.write("Loading data from JSON cache.")
        with open(CACHE_FILE, "r") as f:
            json_data = json.load(f)
            return parse_bls_json(json_data)

    else:
        #if neither exists, fetch data from API
        #st.write("Fetching data from API.")
        headers = {'Content-type': 'application/json'}
        data = json.dumps({
            "seriesid": ['LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001'],
            "startyear": "1994", 
            "endyear": str(current_year)
        })
        response = requests.post(
            'https://api.bls.gov/publicAPI/v1/timeseries/data/',
            data=data,
            headers=headers
        )
        response.raise_for_status()  #raise error for failed requests
        json_data = response.json()

        #save the JSON response locally
        with open(CACHE_FILE, "w") as f:
            json.dump(json_data, f)

        #parse and save to CSV
        df = parse_bls_json(json_data)
        df.to_csv(CSV_FILE, index=False)
        return df

#function to parse BLS JSON data into a DataFrame
def parse_bls_json(json_data):
    #create an empty list to store parsed data
    parsed_data = []

    #mapping for periods to months
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

    #create and return a DataFrame
    return pd.DataFrame(parsed_data)

#fetch and parse the BLS data
df = fetch_bls_data_offline()

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
    'LNS12000000': 'Civillian Employment*',
    'LNS13000000': 'Civillian Unemployment*',
    'LNS14000000': 'Unemployment Rate',
    'CES0000000001': 'Total Nonfarm Employment*'
    }, inplace=True)

#convert 'year' from a string to a number to be able to apply a filter
sorted_df['year'] = pd.to_numeric(sorted_df['year'])

#create a slider to filter the data
year_range = st.slider(
    'Filter data by year:',
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

#create two columns to divide elements on the Streamlit app
left_column, right_column = st.columns(2)

#define each column
with left_column:
  st.subheader("BLS Employment Data, 1984-Present")
  st.dataframe(filtered_df)
  st.caption("_*in Thousands_")

with right_column:
  st.subheader("Unemployment Rate by Month")
  st.line_chart(filtered_df, x='Date', y='Unemployment Rate')
  st.caption("This is a caption")