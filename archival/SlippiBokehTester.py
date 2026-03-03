# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 10:58:16 2025

@author: Hugh Sharp
"""

import json
from json import tool
from re import T
import numpy as np
import pandas as pd

def columnize(rows):
    if not rows:
        return {}

    cols = {key: [] for key in rows[0].keys()}

    for row in rows:
        for key, val in row.items():
            cols[key].append(val)
            
    return cols

def replace_none(x): #for ease of math operations I want the None's to be nan's
    if x is None:
        return float('nan')
    if isinstance(x, list):
        return [replace_none(v) for v in x]
    if isinstance(x, dict):
        return {k: replace_none(v) for k, v in x.items()}
    return x


def load_data(path):

    with open(path, "r") as f:
        data = json.load(f)

    #column_data = columnize(data)

    return replace_none(data)

#test = load_data('C:/Users/Hugh Sharp/Documents/GitHub/SlippiDV/SlippiDV_FullData.json')
rows = load_data('C:/Users/Hugh Sharp/Documents/GitHub/SlippiDV/SlippiDV_FullData.json')
df = pd.DataFrame(rows)
df["matchStartTime"] = pd.to_datetime(df["matchStartTime"], utc=True)

agg = df.groupby("userChar").agg(
total_games=("userChar", "size"),
win_rate=("matchResult", "mean"),
avg_kill_dmg=("userDPS", "mean"),
avg_death_dmg=("oppDPS", "mean"),
avg_dpo=("userDPO", "mean"),
avg_damage=("userDmg", "mean"),
avg_nwr=("userNWR", "mean"),
avg_opk=("userOPK", "mean"),
avg_ocr=("userOCR", "mean"),
avg_time=("gameTime", "mean"))
#inserting bokeh code below

from bokeh.layouts import column, row, layout
from bokeh.models import ColumnDataSource, Select, Slider, DateSlider, Tabs, Panel, FactorRange
from bokeh.plotting import figure
import pandas as pd
from bokeh.io import curdoc
#from assets.CharDefiner import CharacterBar

#will eventually call from its own py file as to be less bloated...
def CharacterBar(xs):
    charMap = {
        "0": "Captain Falcon",
        "1": "Donkey Kong",
        "2": "Fox",
        "3": "Mr. Game & Watch",
        "4": "Kirby",
        "5": "Bowser",
        "6": "Link",
        "7": "Luigi",
        "8": "Mario",
        "9": "Marth",
        "10": "Mewtwo",
        "11": "Ness",
        "12": "Peach",
        "13": "Pikachu",
        "14": "Ice Climbers",
        "15": "Jigglypuff",
        "16": "Samus",
        "17": "Yoshi",
        "18": "Zelda",
        "19": "Sheik",
        "20": "Falco",
        "21": "Young Link",
        "22": "Dr. Mario",
        "23": "Roy",
        "24": "Pichu",
        "25": "Ganondorf"
        }

    colorMap = {
        "0": "#564c91",
        "1": "#9c4c2b",
        "2": "#f0a818",
        "3": "#a8a8a8",
        "4": "#f379ae",
        "5": "#42682b",
        "6": "#0d4a0c",
        "7": "#08c515",
        "8": "#c2240c",
        "9": "#36687d",
        "10": "#b4b6d4",
        "11": "#f0c183",
        "12": "#ea4e82",
        "13": "#fbf10c",
        "14": "#bc9261",
        "15": "#ffd1de",
        "16": "#ff9121",
        "17": "#5bf55b",
        "18": "#b177af",
        "19": "#8d90f5",
        "20": "#3c4e9d",
        "21": "#089b08",
        "22": "#6b676e",
        "23": "#792d29",
        "24": "#fefe7e",
        "25": "#706157"
        }

    charList = [charMap[i] for i in xs]
    colorList = [colorMap[i] for i in xs]
    return charList, colorList

def overview_tab(df):

    character_color = {
        ""
        }


    axis_map_player = {
        "Total Games": "total_games",
        "W/L Ratio": "win_rate",
        "Avg Kill %": "avg_kill_dmg",
        "Avg Death %": "avg_death_dmg",
        "Avg Damage Per Opening": "avg_dpo",
        "Avg Damage Per Game": "avg_damage",
        "Avg Opening Conversion Rate": "avg_ocr",
        "Avg Openings Per Kill": "avg_opk",
        "Avg Neutral Win Rate": "avg_nwr",
        "Avg Game Time (s)": "avg_time"
        }

    #Widgets
    timeSlider = DateSlider(start=df["matchStartTime"].min(), end=df["matchStartTime"].max(), value = df["matchStartTime"].min())
    selAxis_player = Select(title="Player Graph Statistic", options=list(axis_map_player.keys()), value="Total Games")

    #initiate sources
    source_player = ColumnDataSource(data=dict(x=[], 
                                               counts=[],
                                               stat=[],
                                               games=[],
                                               color=[]
                                               ))
    source_player_icons = ColumnDataSource(data=dict(x=[], 
                                               y=[],
                                               icons=[]
                                               ))

    #Define hover tools (tooltips)
    TOOLTIPS_player = [
    ("Statistic", "@stat"),
    ("Games Played", "@games")
    ]

    #Create Plots
    p_player = figure(height = 400, width = 800, x_range=FactorRange(), tools="save", tooltips=TOOLTIPS_player, toolbar_location="right", title="Player Character Stats")
    p_player.vbar(x="x", top="counts", color="color", width=0.9, source=source_player)
    p_player.image_url(url='icons', x='x', y='y', w=0.6, h=0.6, anchor="bottom_center", source=source_player_icons)
    p_player.xaxis.axis_label = "Character"


    #Define what data is currently displayed (i.e. selected)
    def selected_data():
        # Convert slider float (ms since epoch) to a pandas Timestamp
        slider_time = pd.to_datetime(timeSlider.value, unit="ms", utc=True)

        # Filter the DataFrame
        selected = df[df["matchStartTime"] >= slider_time]

        return selected

    def update():
        #define new df
        df_selected = selected_data()
        player_axis = axis_map_player[selAxis_player.value]
        
        p_player.yaxis.axis_label = selAxis_player.value

        #aggregate stats
        agg = df_selected.groupby("userChar").agg(
        total_games=("userChar", "size"),
        win_rate=("matchResult", "mean"),
        avg_kill_dmg=("userDPS", "mean"),
        avg_death_dmg=("oppDPS", "mean"),
        avg_dpo=("userDPO", "mean"),
        avg_damage=("userDmg", "mean"),
        avg_nwr=("userNWR", "mean"),
        avg_opk=("userOPK", "mean"),
        avg_ocr=("userOCR", "mean"),
        avg_time=("gameTime", "mean"))
        
        agg = agg.sort_values(by=player_axis, ascending = False)
        
        #grab final lists
        xs = agg.index.astype(str).tolist()
        count = agg[player_axis].tolist()
        chars, colors = CharacterBar(xs)
        iconlist = ["static/Character/" + j + ".png" for j in xs]

        source_player.data = dict(
            x=chars,
            counts=count,
            stat=count,
            games=agg["total_games"].tolist(),
            color=colors
            )
        
        source_player_icons.data = dict(
            x=chars,
            y=[i + 0.1*max(count) for i in count],
            icons=iconlist
            )

        # SET OR UPDATE THE X-RANGE FACTORS
        p_player.x_range.factors = chars

    controls = [timeSlider, selAxis_player]
    for control in controls:
        control.on_change('value', lambda attr, old, new: update())

    inputs = column(*controls, width=500, height=500)
    inputs.sizing_mode = "fixed"

    update()  # initial load of the data
    
    l = layout([
        [p_player, inputs],
    ], sizing_mode="scale_both")
    
    return l
        
# this would be in app.py
tabs = Tabs(tabs=[
    Panel(child=overview_tab(df), title="Overview")
])

curdoc().add_root(tabs)
curdoc().theme = 'dark_minimal'
curdoc().template = """
{% block postamble %}
<style>

    /* -------------------------------
     *   GLOBAL MELEE DARK BACKGROUND  
     * ------------------------------- */
    body {
        background-color: #0f1026; /* melee deep blue/purple */
        color: #dcdcdc;
        font-family: 'Verdana', sans-serif;
    }

    .bk-root {
        background-color: #0f1026 !important;
        color: #e6e6e6;
    }

    /* Panels, layouts */
    .bk-layout-fixed, .bk-panel {
        background-color: #141533 !important;
        border-radius: 8px;
        padding: 6px;
        box-shadow: 0 0 12px rgba(0,0,0,0.6);
    }

    /* -------------------------------
     *   TEXT & LABELS (Melee white/gray)
     * ------------------------------- */
    .bk-slider-title,
    .bk-input-group label,
    .bk-select option{
        color: #ececec !important;
        font-weight: 600;
    }

    /* -------------------------------
     *   INPUTS (sliders, textboxes, selects)
     *   Background: melee navy
     *   Highlight: electric blue
     * ------------------------------- */
    .bk-input, 
    .bk-select, 
    .bk-slider-value {
        background-color: #1a1b3d !important;
        color: #f0f0f0 !important;
        border: 2px solid #2d2e56 !important;
        border-radius: 6px;
        font-weight: 600;
    }

    .bk-input:focus, 
    .bk-select:focus {
        border-color: #2a66ff !important; /* Melee highlight blue */
        box-shadow: 0 0 8px rgba(42,102,255,0.6);
    }

    /* -------------------------------
     *   BUTTONS (Melee gold + blue)
     * ------------------------------- */
    .bk-button {
        background-color: #33345e !important;
        color: #f7d778 !important; /* melee gold */
        border: 2px solid #f0c84b !important;
        border-radius: 8px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: 0.15s;
    }

    .bk-button:hover {
        background-color: #2a2b50 !important;
        box-shadow: 0 0 10px rgba(255, 206, 72, 0.7); /* gold glow */
        color: #ffe18a !important;
    }

    /* -------------------------------
     *   SLIDERS (Melee highlight blue)
     * ------------------------------- */
    .bk-noUi-target {
        background: #1a1b3d !important;
        border: 2px solid #2d2e56 !important;
        border-radius: 8px;
    }

    .bk-noUi-connect {
        background: #2a66ff !important; /* electric blue */
    }

    .bk-noUi-handle {
        background: #f7d778 !important; /* gold handle */
        border: 2px solid #c89d20 !important;
        box-shadow: 0 0 10px rgba(255,206,72,0.5);
    }

    /* -------------------------------
     *   TABS (blue highlight + gold hover)
     * ------------------------------- */
    .bk-tabs-header {
        background-color: #141533 !important;
        border-bottom: 2px solid #2d2e56 !important;
    }

    .bk-tab {
        background-color: #141533 !important;
        color: #e6e6e6 !important;
        font-weight: 700;
        padding: 8px 12px;
        border-radius: 6px 6px 0 0;
        transition: 0.15s;
    }

    .bk-tab:hover {
        background-color: #1d1e49 !important;
        color: #ffe18a !important;   /* gold hover */
    }

    .bk-tab.bk-active {
        background-color: #1d1e49 !important;
        color: #2a66ff !important;   /* melee blue active */
        border-bottom: 3px solid #2a66ff !important;
        font-weight: 800;
    }

    .bk-Tooltip {
    background-color: #222222; !important /* Dark background */
    color: #ffffff; !important /* White text */
    }

</style>
{% endblock %}
"""
curdoc().title = "Data Visualizer"
"""
# this would be in main.py
import subprocess
import sys
import time
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl


qt_app = QApplication([])

bokeh_proc = subprocess.Popen([
    sys.executable, "-m", "bokeh", "serve", "app",
    "--allow-websocket-origin=localhost:5006",
])

# Give server time to start
time.sleep(2)

view = QWebEngineView()
view.load(QUrl("http://localhost:5006/app"))
view.setWindowTitle("Data Visualizer")
view.show()

qt_app.exec_()

# Close Bokeh server when Qt exits
bokeh_proc.terminate()
"""