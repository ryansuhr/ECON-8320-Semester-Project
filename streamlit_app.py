import streamlit as st

st.title("🎈 My new Streamlit app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

import requests
import json
import pandas as pd

#requesting the data
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": ['LNS12000000','LNS13000000','LNS14000000','CES0000000001'],"startyear":"2023", "endyear": "2024"})
p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
json_data = json.loads(p.text)

#parsing the data
parsed_data = []

for series in json_data['Results']['series']:
    series_id = series['seriesID']
    for item in series['data']:
        year = item['year']
        period = item['period']
        value = item['value']
        
        #add footnotes?

        parsed_data.append({
            "series_id": series_id,
            "year": year,
            "period": period,
            "value": value,
        })

#creating the DataFrame
df = pd.DataFrame(parsed_data)

df.to_csv('bls_data.csv', index=False)