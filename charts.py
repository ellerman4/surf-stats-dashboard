
from streamlit_echarts import st_echarts, st_pyecharts
from st_aggrid import AgGrid
import numpy as np
import pandas as pd
from pyecharts.charts import Bar
import pyecharts.options as opts
import streamlit as st
import base64

def draw_pie(df):
    options = {
        "tooltip": {"trigger": "item"},
        "legend": {"top": "0%", "left": "center",
                "textStyle": { "color": "white"}},
        "series": [
            {
                "name": "maps_pie",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2,
                },
                "label": {"show": False, "position": "center"},
                "emphasis": {
                    "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                },
                "labelLine": {"show": False},
                "data": [
                    {"value": df.shape[0], "name": "Maps Completed", "itemStyle": {"color": "#4173bf"}},
                    {"value": (944 - df.shape[0]), "name": "Maps Left", "itemStyle": {"color": "#b06161"}},
                ],
            }
        ],
    }
    st_echarts(
        options=options, height="495px",
    )

def draw_bonus_pie(bonus_completion):
    bonus_df = pd.read_csv('./data/map_bonuses.csv')

    bonus_total = bonus_df['Bonuses'].sum()

    bonus_left = bonus_total - int(bonus_completion)

    options = {
        "tooltip": {"trigger": "item"},
        "legend": {"top": "0%", "left": "center",
                "textStyle": { "color": "white"}},
        "series": [
            { 
                "name": "maps_pie",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2,
                },
                "label": {"show": False, "position": "center"},
                "emphasis": {
                    "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                },
                "labelLine": {"show": False},
                "data": [
                    {"value": int(bonus_completion), "name": "Bonuses Completed", "itemStyle": {"color": "#4173bf"}},
                    {"value": int(bonus_left), "name": "Bonuses Left", "itemStyle": {"color": "#b06161"}},
                ],
            }
        ],
    }
    st_echarts(
        options=options, height="495px"
    )


def draw_table(df):
    custom_css = {
    '.ag-header-cell-label': {'justify-content': 'center'},
    '.ag-theme-streamlit .ag-root-wrapper': {'text-align': 'center'},
    '.ag-theme-streamlit .ag-ltr .ag-cell': {'text-align': 'center'}
    }
    AgGrid(df, theme="streamlit", custom_css=custom_css)


def draw_bar(df):
    # Assign count of Map Tiers to respective variables
    tier1, tier2 = np.sum(df['Map Tier'] == 1), np.sum(df['Map Tier'] == 2)
    tier3, tier4 = np.sum(df['Map Tier'] == 3), np.sum(df['Map Tier'] == 4)
    tier5, tier6 = np.sum(df['Map Tier'] == 5), np.sum(df['Map Tier'] == 6)
    
    options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "0%", "left": "center"},
    "xAxis": {
        "type": "category",
        "data": ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6"],
    },
    "yAxis": {"type": "value"},
    "series": [
        {"data": [
            {"value": int(tier1), "itemStyle": {"color": "#b06161"}},   
            {"value": int(tier2), "itemStyle": {"color": "#b0ad61"}},
            {"value": int(tier3), "itemStyle": {"color": "#8ab061"}},   # Echarts cant read np64 integers, convert to regular int
            {"value": int(tier4), "itemStyle": {"color": "#61b094"}},
            {"value": int(tier5), "itemStyle": {"color": "#616ab0"}},
            {"value": int(tier6), "itemStyle": {"color": "#a561b0"}}
            ],
                "type": "bar"}
            ],  
    }
    st_echarts(options=options, height="515px")


def players_bar():
    range_color = ['#4173bf', '#7567b4', '#965a9f', '#aa4f85', '#b24a68', '#b04c4c']

    top_players = pd.read_csv('./data/top_players.csv').drop(columns=['Unnamed: 0'])

    top_points = int(top_players['Points'].iloc[0])
    bottom_points = int(top_players['Points'].iloc[-1])

    b = (
        Bar()
        .add_xaxis(top_players['Player Name'].tolist())
        .add_yaxis('Points', top_players['Points'].tolist())
        .set_series_opts(label_opts=opts.LabelOpts(color='#ffffff'))
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                min_=bottom_points,
                max_=top_points,
                range_color=range_color,
                pos_top="80"),
            title_opts=opts.TitleOpts(
                title="Top 25 players by points", subtitle="Points", title_link='https://snksrv.com/surfstats/?view=players',
                title_textstyle_opts=opts.TextStyleOpts(color='#ffffff',font_size=20, font_family='monospace'),
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=True)
            ),
        )
    )
    st_pyecharts(b, height=480)


countries = {
    'Canada': 'ca',
    'The United States': 'us',
    'The United Kingdom': 'gb',
    'Denmark': 'dk',
    'Japan': 'jp',
    'Russia': 'ru',
    'Finland': 'fl',
    'Australia': 'au',
    'Norway': 'no',
    'Germany': 'de',
    'The Netherlands': 'nl',
    'Sweden': 'se',
    'Belgium': 'be',
    'Hong Kong': 'hk',
    'Poland': 'pl',
}


# Custom css for player name and country flag
def draw_flag(player_name, player_country, id64):

    # Loop through countries until a match is found
    for k,v in countries.items():
        if k in player_country:
            flag = f"./assets/flags/{v}.png"
        else:
            flag = "./assets/flags/us.png"

    # Some css hacking with text animation
    st.markdown(
        """
        <style>
        .container {
            display: flex;
        }
        .logo-text {
            font-weight:700 !important;
            font-size:50px !important;
            color: #FAFAFA !important;
            padding-top: 75px !important;
            padding-right: 15px !important;
            -webkit-animation: tracking-in-expand 0.7s cubic-bezier(0.215, 0.610, 0.355, 1.000) both !important;
            animation: tracking-in-expand 0.7s cubic-bezier(0.215, 0.610, 0.355, 1.000) both;
        }
        
        @-webkit-keyframes tracking-in-expand {
        0% {
            letter-spacing: -0.5em;
            opacity: 0;
        }
        40% {
            opacity: 0.6;
        }
        100% {
            opacity: 1;
        }
        }
        @keyframes tracking-in-expand {
        0% {
            letter-spacing: -0.5em;
            opacity: 0;
        }
        40% {
            opacity: 0.6;
        }
        100% {
            opacity: 1;
            }
        }

        .logo-img {
            float:right;
            height: 29px !important;
            margin-top: 100px;
        }
        .css-13sdm1b a {
            color: rgb(191 109 109);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="container">
            <p class="logo-text">
                <a href="http://steamcommunity.com/profiles/{id64}">{player_name}</a>'s surf stats
            </p>
            <img class="logo-img" title="Country" src="data:image/png;base64,{base64.b64encode(open(flag, "rb").read()).decode()}">
        </div>
        """,
        unsafe_allow_html=True
    )


ranks = {
    'NEWBIE': 0,
    'AMATEUR': 87,
    'NOVICE': 604,
    'APPRENTICE': 2154,
    'CASUAL': 5170,
    'REGULAR': 10340,
    'ADVANCED': 21540,
    'ADVANCED+': 38772,
    'SEMI-ELITE': 58589,
    'ELITE': 74960,
    'VETERAN': 86160,
    'SEMI-PRO': 107700,
    'PRO': 137856,
    'AMAZING': 189552,
    'STUNNING': 215400,
    'MASTER': 241248,
    'WICKED': 267096,
    'INSANE': 292944,
    'RIDICULOUS': 323100,
    'LEGEND': 353256,
    'SURF GOD': 430800
    }


# Loop through ranks until value greater than player points is found
def draw_rank(points):
    for k,v in ranks.items():
        if v > int(points):
            next_rank = k
            next_rank_points = ranks[k]
            break
        else:
            next_rank = 'NONE'
            next_rank_points = 0
    st.metric(label="Next Rank", value=next_rank, delta = abs(int(points) - next_rank_points), delta_color="off")


# Get players current rank
def draw_current_rank(points):
    # Get current rank
    for k,v in ranks.items():
        if v < int(points):
            current_rank = k
    st.metric(label="Current Rank", value=current_rank, delta=points)
