import streamlit as st
import pandas as pd
from charts import draw_pie, draw_table, draw_bar, draw_flag, players_bar, draw_rank, draw_current_rank, draw_bonus_pie
import Converter
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
from css.custom_css import button_css
import psycopg2
from datetime import datetime
import timeit
from bs4 import BeautifulSoup
import requests
from css.streamlit_download_button import download_button

# Create a runtime error if user enters an invalid SteamID
invalid_id = RuntimeError('You may have entered an invalid SteamID')

st.set_page_config(layout="wide")


# Initialize connection to database
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

# Create a cursor to interact with the database
conn = init_connection()
cur = conn.cursor()

# Load some custom css
button_css()


# Fix padding
st.markdown('''
    <style>
    .css-18e3th9 {
        padding: 0rem 1rem 10rem;
        flex: 1 1 0%;
        width: 100%;
        padding-left: 5rem;
        padding-right: 5rem;
        min-width: auto;
        max-width: initial;
        top: 15px;
    }
    </style>''',
    unsafe_allow_html=True
    )


# Build a sidebar for user input
with st.sidebar:
    #card()
    st.title("Sneakz web scraper")
    text_input = st.text_input(label='Enter your Steam ID').strip()
    submit_button = st.button(label='Scrape')
    st.subheader('SteamID Examples:')
    st.info('''Legacy SteamID: STEAM_1:1:171196293
                SteamID64: 76561198302658315
                SteamID3: [U:1:342392587]''')

# Stops the entire process until submit_button is clicked
if not submit_button:
    st.stop()

# Start a timer to log scrape time
start = timeit.default_timer()


# Initialize streamlit spinner animation while scraping data
with st.spinner('Retrieving Surf Stats...'):
    try:
        s_id = Converter.to_steamID(text_input)
        id64 = Converter.to_steamID64(text_input)
    except:
        st.exception(invalid_id)
        st.stop()
    
    data = requests.get(f"https://snksrv.com/surfstats/?view=profile&id={s_id}").text
    soup = BeautifulSoup(data, 'html.parser')

    # Get general player data
    player_name = soup.find('h2').text
    points = soup.find('td').text[8:]
    player_country = soup.find('b', string="Country").next_sibling.text[2:]
    player_rank = soup.find('b').text[6:]
    bonus_completion = soup.find('b', string="Bonus Completions").next_sibling.text[2:]

    map_records = soup.find('b', string="Map Records").next_sibling.text[2:]
    bonus_records = soup.find('b', string="Bonus Records").next_sibling.text[2:]
    stage_records = soup.find('b', string="Stage Records").next_sibling.text[2:]

    # Get player map time data with pandas built in read_html function
    table = soup.find_all('table')
    df = pd.read_html(str(table))[2]

# Stop the timer and calculate execution time
stop = timeit.default_timer()
execution_time = stop - start


# Delete row by steamid if exists
cur.execute("DELETE FROM player_stats WHERE steamid = %s",(s_id,))

# Insert player stats into database
cur.execute("""INSERT INTO player_stats(name, steamid, points, map_records, date, rank, country)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (player_name, s_id, points, map_records, datetime.today(), player_rank, player_country))

# Commit database changes
conn.commit()


#Create dataframe from the result list
#df = pd.DataFrame(result)
df['Rank'] = pd.to_numeric(df['Rank'])  # Convert rank column to numeric for accurate sorting/filtering

# Read maps.csv with map name and map tier data
maps_df = pd.read_csv('./data/maps.csv')

# Merge player stats with map tier on Map Name column
df = pd.merge(df, maps_df, on='Map Name')


# Start building the dashboard when scraping is complete
draw_flag(player_name, player_country, id64)


if int(player_rank) <= 100:
    st.markdown(f"Rank:  {player_rank}  ⚡")
else:
    st.markdown(f"Rank:  {player_rank}")

# Create columns for records
map_col, bonus_col, stage_col= st.columns(3)


with map_col:
    draw_current_rank(points)

with bonus_col:
    draw_rank(points)

# Include tooltip info for records via inline html
with stage_col:
    st.markdown(f'''<div class="tooltip",
                    style="cursor:pointer;
                            margin-left: -877px;
                            margin-top: 71px;",
                    title="Records">🥇{map_records} 🥈{bonus_records} 🥉{stage_records}</div>''',
                unsafe_allow_html=True)


# Create a column layout table and bar chart
table_col, chart_col = st.columns(2)

# Create a column for pie charts
pie_col1, pie_col2 = st.columns(2)

# Convert dataframe to csv
@st.cache(ttl=300, max_entries=2)
def convert_df(df):
    return df.to_csv().encode('utf-8')


# Draw table and download button in table column
with table_col:
    st.markdown(
        download_button(convert_df(df), "surf_stats.csv", "Press to Download"),     # Load custom download button with a streamlit markdown (re-run workaround)
        unsafe_allow_html=True)

    draw_table(df)

# Draw map tier bar chart
with chart_col:
    draw_bar(df)


# Pie charts in dedicated columns under table/bar chart columns
with pie_col1:
    draw_pie(df)

with pie_col2:
    draw_bonus_pie(bonus_completion)


# Display top 25 players bar chart under a markdown
st.markdown('***')
players_bar()

# Create a profile report
pr = df.profile_report()

# Create expander for pandas profile report
with st.expander("See Profile Report"):
    st_profile_report(pr, key='profile-report')

    st.download_button(label="Download Full Report", data=pr.to_html(), file_name='report.html')

# Write execution time
st.write(execution_time)