import streamlit as st

st.title("🎈 My new Streamlit app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

import requests
import json
import pandas as pd

#request the data
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": ['LNS12000000','LNS13000000','LNS14000000','CES0000000001'],"startyear":"2023", "endyear": "2024"})
p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
json_data = json.loads(p.text)

#parse the data
parsed_data = []

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

for series in json_data['Results']['series']:
    series_id = series['seriesID']
    for item in series['data']:
        year = item['year']
        period = item['period']
        value = item['value']

        month = period_to_month.get(period, None)

        parsed_data.append({
            "series_id": series_id,
            "year": year,
            "period": period,
            "month": month,
            "value": value,
        })

#creating the DataFrame
df = pd.DataFrame(parsed_data, index=None, columns=['year', 'month', 'series_id', 'value'])
df.to_csv('bls_data.csv', index=False)

pivot_df = df.pivot(index=['year', 'month'], columns='series_id', values='value')
pivot_df = pivot_df.reset_index()

pivot_df['Date'] = pd.to_datetime(pivot_df['year'].astype(str) + '-' + pivot_df['month'].astype(str))
sorted_df = pivot_df.sort_values(by=['Date'])
#sorted_df = sorted_df.drop(columns=['Date']) Can uncomment this to drop the date column, if desired
sorted_df.reset_index(drop=True, inplace=True)
sorted_df