# -*- coding: utf-8 -*-
"""
THIS IS THE TEST FILE FOR SLIPPI BOKEH TESTER NOT MAIN FOR THE APP
"""

import json
from json import tool
from re import T
from tkinter import SEL
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

###########################################################################################################################################
#Overview Tab
import os
import base64
from bokeh.layouts import column, row, layout
from bokeh.models import ColumnDataSource, Select, Slider, DateSlider, Tabs, Panel, FactorRange, Range1d, Div
from bokeh.plotting import figure
import pandas as pd
from bokeh.io import curdoc
#from assets.CharDefiner import CharacterBar

#will eventually call from its own py file as to be less bloated...

#used in assigning name and color to charID
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

# Helper to convert PNG to base64 to be able to call/update icons dynamically
def png_to_base64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def overview_tab(df):
    
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

    axis_map_opp = {
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

    #used when filtering data by character
    CharacterSelect = {
        "All": "All",
        "Captain Falcon": "0",
        "Donkey Kong": "1",
        "Fox": "2",
        "Mr. Game & Watch": "3",
        "Kirby": "4",
        "Bowser": "5",
        "Link": "6",
        "Luigi": "7",
        "Mario": "8",
        "Marth": "9",
        "Mewtwo": "10",
        "Ness": "11",
        "Peach": "12",
        "Pikachu": "13",
        "Ice Climbers": "14",
        "Jigglypuff": "15",
        "Samus": "16",
        "Yoshi": "17",
        "Zelda": "18",
        "Shiek": "19",
        "Falco": "20",
        "Young Link": "21",
        "Dr. Mario": "22",
        "Roy": "23",
        "Pichu": "24",
        "Ganondorf": "25"
        }

    #Widgets
    timeSlider = DateSlider(start=df["matchStartTime"].min(), end=df["matchStartTime"].max(), value = df["matchStartTime"].min(), title="Lookback Time")
    minGamesSlider = Slider(start=0, end=50, value = 0, title="Mininum Played Games (Data Cut Off)")
    selAxis_player = Select(title="Player Graph Statistic", options=list(axis_map_player.keys()), value="Total Games")
    selAxis_opp = Select(title="Matchup Graph Statistic", options=list(axis_map_opp.keys()), value="W/L Ratio")
    selChar_opp = Select(title="Filter Bottom Graph by Player Character", options=list(CharacterSelect.keys()), value="All")

    

    #initiate player sources
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

    #initiate Opponent sources
    source_opp = ColumnDataSource(data=dict(x=[], 
                                               counts=[],
                                               stat=[],
                                               games=[],
                                               color=[]
                                               ))
    source_opp_icons = ColumnDataSource(data=dict(x=[], 
                                               y=[],
                                               icons=[]
                                               ))
    #Create errmsg_box
    errmsg_box = Div(width = 300)

    #Create stat_box
    stat_box = Div(width = 300, text="")

    #Define hover tools (tooltips)
    TOOLTIPS_player = [
    ("Statistic", "@stat"),
    ("Games Played", "@games")
    ]

    TOOLTIPS_opp = [
    ("Current Statistic", "@stat"),
    ("Games Played", "@games")
    ]

    #Create Plots
    p_player = figure(height = 450, width = 800, x_range=FactorRange(), y_range=Range1d(), tools="save,undo,redo,box_zoom", tooltips=TOOLTIPS_player, toolbar_location="right", title="Sorted By Player Character")
    p_player.vbar(x="x", top="counts", color="color", width=0.9, source=source_player)
    p_player.image_url(url='icons', x='x', y='y', w=40, h=40, w_units="screen", h_units="screen", anchor="bottom_center", source=source_player_icons)
    p_player.xaxis.axis_label = "Character"

    p_opp = figure(height = 450, width = 800, x_range=FactorRange(), y_range=Range1d(), tools="save,undo,redo,box_zoom", tooltips=TOOLTIPS_opp, toolbar_location="right", title="Sorted By Opponent Character")
    p_opp.vbar(x="x", top="counts", color="color", width=0.9, source=source_opp)
    p_opp.image_url(url='icons', x='x', y='y', w=40, h=40, w_units="screen", h_units="screen", anchor="bottom_center", source=source_opp_icons)
    p_opp.xaxis.axis_label = "Character"
    #############################
    #       ICONS AAAAA         #
    #############################

    # Preload all icons as Base64
    static_folder = "SlippiBokehTester/static/Character/"
    icons_base64 = [png_to_base64(os.path.join(static_folder, f"{i}.png")) for i in range(0, 26)]

    #NEEDED TO KEEP CONSISTENT ICON WIDTH
    CharsPlayed = len(df.groupby("userChar").agg( total_games=("userChar", "size"))["total_games"].tolist()) #prolly inefficient lmao
    CharsPlayed_opp = len(df.groupby("oppChar").agg( total_games=("oppChar", "size"))["total_games"].tolist())

    #Define what data is currently displayed (i.e. selected)
    def selected_by_game():
        # Convert slider float (ms since epoch) to a pandas Timestamp
        slider_time = pd.to_datetime(timeSlider.value, unit="ms", utc=True)
        
        # Filter the DataFrame
        selected = df[df["matchStartTime"] >= slider_time ]
        
        if selChar_opp.value == "All":
            #print("ALL")
            selected_opp = selected
        else:
            selected_opp = selected[selected["userChar"] == selChar_opp.value]

        return selected

    
    def Char_Filter(df_old, xs): #returns error statement if filtering by a character you haven't played
        #Current bugs: 
        #doesn't change data in plot when selecting valid character.
        #still returns df of size 0 when selecting invalid character, BUT displays correct error message.

        charID_now = CharacterSelect[selChar_opp.value]

        if charID_now == "All":
            #print(df_old)
            return df_old, ''
        elif charID_now not in xs:
            #print(df_old)
            return df_old, 'ERROR: Currently NO games filtered character. Displaying all games instead.'
        else:
            df_new = df_old[df_old["userChar"] == int(charID_now)]
            #print(df_old[df_old["userChar"] == charID_now])
            #print(df_new == df_old)
            return df_new, ''
          

    def selected_by_stat(agg_old):

        
        agg_selected = agg_old[agg_old['total_games'] > minGamesSlider.value] 
                               

        return agg_selected

    def update():
        #define new df filtering by game properties
        df_selected = selected_by_game()
        

        #Player Sorted Data
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
        
        #define new df filtering by statistic properties
        agg = selected_by_stat(agg)

        agg = agg.sort_values(by=player_axis, ascending = False)
        
        #grab final lists
        xs = agg.index.astype(str).tolist()
        count = agg[player_axis].tolist()
        chars, colors = CharacterBar(xs)
        iconlist = [icons_base64[int(c)] for c in xs]

        #setting image scale (surprising changes dependent on where it s placed on graph omg)
        #iconWidth = [0.6 * len(xs)/CharsPlayed for i in count]
        #iconHeight = [0.6 * max(count)/4 for i in count]

        source_player.data = dict(
            x=chars,
            counts=count,
            stat=count,
            games=agg["total_games"].tolist(),
            color=colors
            )
        
        source_player_icons.data = dict(
            x=chars,
            y=[i + 0.05*max(count) for i in count],
            icons=iconlist
            )

        # SET OR UPDATE THE X-RANGE FACTORS
        

        p_player.x_range.factors = chars
        p_player.y_range.end = max(count)*1.25

        #Opponent Sorted Data
        df_selected_opp, err_text = Char_Filter(df_selected, xs)

        opp_axis = axis_map_opp[selAxis_opp.value]
        p_opp.yaxis.axis_label = selAxis_opp.value
        

        agg_opp = df_selected_opp.groupby("oppChar").agg(
        total_games=("oppChar", "size"),
        win_rate=("matchResult", "mean"),
        avg_kill_dmg=("userDPS", "mean"),
        avg_death_dmg=("oppDPS", "mean"),
        avg_dpo=("userDPO", "mean"),
        avg_damage=("userDmg", "mean"),
        avg_nwr=("userNWR", "mean"),
        avg_opk=("userOPK", "mean"),
        avg_ocr=("userOCR", "mean"),
        avg_time=("gameTime", "mean"))

        agg_opp = selected_by_stat(agg_opp)

        agg_opp = agg_opp.sort_values(by=opp_axis, ascending = False)
        

        #grab final lists
        xs_opp = agg_opp.index.astype(str).tolist()
        count_opp = agg_opp[opp_axis].tolist()
        chars_opp, colors_opp = CharacterBar(xs_opp)
        iconlist_opp = [icons_base64[int(c)] for c in xs_opp]
        
        #setting image scale (surprising changes dependent on where it s placed on graph omg)
        #iconWidth_opp = [0.6 * len(xs_opp)/CharsPlayed_opp for i in count_opp]
        #iconHeight_opp = [0.6 * max(count_opp)/4 for i in count_opp]
        
        source_opp.data = dict(
            x=chars_opp,
            counts=count_opp,
            stat=count_opp,
            games=agg_opp["total_games"].tolist(),
            color=colors_opp
            )
        
        source_opp_icons.data = dict(
            x=chars_opp,
            y=[i + 0.05*max(count_opp) for i in count_opp],
            icons=iconlist_opp
            )
        
        # SET OR UPDATE THE X-RANGE FACTORS
        p_opp.x_range.factors = chars_opp
        p_opp.y_range.end = max(count_opp)*1.25

        
        #initiate table
        stats = {
                "Total Games": agg["total_games"].sum(),
                "Win Rate": df_selected["matchResult"].mean(), #really should do a weighted avg of win rate in agg
                "User input/min": df_selected["userIPM"].mean(),
                "Opp. input/min": df_selected["oppIPM"].mean(),
                "User L-Cancel Rate": df_selected["userLCR"].mean(),
                "Opp. L-Cancel Rate": df_selected["oppLCR"].mean(),
                "User Wavedash/Game": df_selected["userWaveDash"].mean(),
                "Opp. Wavedash/Game": df_selected["oppWaveDash"].mean(),
                "User Dashdance/Game": df_selected["userDashDance"].mean(),
                "Opp. Dashdance/Game": df_selected["oppDashDance"].mean(),
                "User Grab/Game": df_selected["userGrab"].mean(),
                "Opp. Grab/Game": df_selected["oppGrab"].mean()
            }
        items = "".join([f"<div class='item'><b>{k}</b>: {v:.2f}</div>" 
                     for k, v in stats.items()])
        html = f"""
        <div style="
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px 20px;
            font-family: Arial;
            font-size: 14px;
            color: #eee;">
            {items}
        </div>
        """
        
        # update the Div
        stat_box.text = html

        #update errormsg
        errmsg_box.text = err_text

    controls = [timeSlider, minGamesSlider, selAxis_player, selAxis_opp, selChar_opp]
    for control in controls:
        control.on_change('value', lambda attr, old, new: update())

    #Make column for inputs
    inputs = column(*controls, errmsg_box, stat_box, width=300, sizing_mode="fixed")

    #Make column for plots
    plots = column(p_player, p_opp, width=900, sizing_mode="stretch_width")

    update()  # initial load of the data

    layout = row(
    plots,
    inputs,
    sizing_mode="stretch_width",
    width_policy="max"
    )
    
    """
    l = layout([
        [p_player, inputs],
    ], sizing_mode="scale_both")
    """
    return layout
        
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