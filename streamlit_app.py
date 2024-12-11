import streamlit as st
import pandas as pd
import os

#enable wide mode
st.set_page_config(layout="wide")

#path to the data file
CSV_FILE = "/workspaces/ECON-8320-Semester-Project/bls_data.csv"

#load the data
if os.path.exists("/workspaces/ECON-8320-Semester-Project/bls_data.csv"):
    df = pd.read_csv("/workspaces/ECON-8320-Semester-Project/bls_data.csv")
    st.write("Data loaded successfully!")
else:
    st.error("Data file not found. Please run the update script.")

#pivot the DataFrame so that each 'series_id' becomes its own column of values 
pivoted_df = df.pivot(index=['year', 'month'], columns='series_id', values='value')

# Ensure 'year' and 'month' exist in the MultiIndex
if 'year' not in pivoted_df.index.names or 'month' not in pivoted_df.index.names:
    raise ValueError("The pivot operation failed to include 'year' or 'month' in the index.")

#create a 'Date' column for chronological sorting
pivoted_df['Date'] = pd.to_datetime(pivoted_df.index.get_level_values('year').astype(str)
    + '-'
    + pivoted_df.index.get_level_values('month').astype(str))

#use 'Date' to sort the Dataframe chronologically
sorted_df = pivoted_df.sort_values(by=['Date'])

#reset the index ('year' and 'month' are now their own columns - removed from the multiindex)
sorted_df = sorted_df.reset_index()

#convert all data values from strings to numbers for better readability
numeric_columns = ['LNS11000000', 'LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001']
for col in numeric_columns:
    if col in sorted_df.columns:
        sorted_df[col] = pd.to_numeric(sorted_df[col], errors='coerce')

#rename each 'series_id' to its actual name
sorted_df.rename(columns={
    'LNS11000000': 'Civillian Labor Force*',
    'LNS12000000': 'Civillian Employment*',
    'LNS13000000': 'Civillian Unemployment*',
    'LNS14000000': 'Unemployment Rate',
    'CES0000000001': 'Total Nonfarm Employment*'
    }, inplace=True)

#convert 'year' from a string to a number to be able to apply a filter
sorted_df['year'] = pd.to_numeric(sorted_df['year'])

#create a sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page:", ["Welcome Page", "Employment Data", "Unemployment Data"])

#Welcome Page
if page == "Welcome Page":
    st.title("Howdy, stranger! :face_with_cowboy_hat:")
    st.write(
        "Hello, and welcome to my page! Here, I've compiled some employment data from the US Bureau of Labor Statistics. If you use the navigation sidebar to your left, you'll see two pages: one is Employment Data and the other Unemployment Data. Click on one of those to start exploring. Giddy-up!"
    )
#Employment Page
if page == "Employment Data":
    st.title("Employment Data")

    #create a copy of the DataFrame
    empl_df = sorted_df

    #convert 'year' from a string to a number to be able to apply a filter
    empl_df['year'] = pd.to_numeric(empl_df['year'])

    #create a slider to filter the data
    year_range = st.slider(
    'Filter data by year:',
    min_value=int(sorted_df['year'].min()),
    max_value=int(sorted_df['year'].max()),
    value=(int(sorted_df['year'].min()), int(sorted_df['year'].max()))
    )

    #create a filtered copy of the DataFrame for the Employment Data page
    empl_df = empl_df[(empl_df['year'] >= year_range[0]) & (empl_df['year'] <= year_range[1])]

    #convert 'year' back to a string to avoid commas in the DataFrame
    empl_df['year'] = empl_df['year'].astype(str)

        #create another copy specifically for the graph
    emgr_df = empl_df
    emgr_df['Month_Year'] = emgr_df['Date'].dt.strftime('%Y-%m') #format date as YYY-MM

    #drop the Unemployment data and 'Date'
    empl_df.drop(columns=['Civillian Unemployment*','Unemployment Rate', 'Date'], inplace=True)

    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("BLS Employment Data, 1994-Present")
        st.dataframe(empl_df)
        st.caption("_*in Thousands_")

    with right_column:
        st.subheader("Employment Trends")
        st.bar_chart(emgr_df, x='Month_Year', y=['Civillian Labor Force*', 'Civillian Employment*', 'Total Nonfarm Employment*'], stack=False )
        st.caption("This is a caption! Change me or remove me, please!")

#Unemployment Page
elif page == "Unemployment Data":
    st.title("Unemployment Data")

    #create a copy of the DataFrame
    unempl_df = sorted_df

    #convert 'year' from a string to a number to be able to apply a filter
    unempl_df['year'] = pd.to_numeric(unempl_df['year'])

    #create a slider to filter the data
    year_range = st.slider(
    'Filter data by year:',
    min_value=int(sorted_df['year'].min()),
    max_value=int(sorted_df['year'].max()),
    value=(int(sorted_df['year'].min()), int(sorted_df['year'].max()))
    )

    #create a filtered copy of the DataFrame for the Unemployment Data page
    unempl_df = unempl_df[(unempl_df['year'] >= year_range[0]) & (unempl_df['year'] <= year_range[1])]

    #convert 'year' back to a string to avoid commas in the DataFrame
    unempl_df['year'] = unempl_df['year'].astype(str)

     #create another copy specifically for the graph
    ungr_df = unempl_df
    ungr_df['Month_Year'] = ungr_df['Date'].dt.strftime('%Y-%m') #format date as YYY-MM

    #drop the Employment data and 'Date'
    unempl_df.drop(columns=['Total Nonfarm Employment*','Civillian Employment*','Date'], inplace=True)

    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("BLS Unemployment Data, 1994-Present")
        st.dataframe(unempl_df)
        st.caption("_*in Thousands_")

    with right_column:
        st.subheader("Unemployment Rate")
        st.line_chart(ungr_df, x='Month_Year', y='Unemployment Rate')
        st.caption("This is a caption! Change me or remove me, please!")