# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 10:58:16 2025

@author: Hugh Sharp
"""

import json
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
from bokeh.models import ColumnDataSource, Select, Slider, DateSlider, Tabs, Panel
from bokeh.plotting import figure
import pandas as pd
#from bokeh.models.widgets import Tabs, Panel
from bokeh.io import curdoc

def overview_tab(df):

    character_color = {
        ""
        }


    axis_map_player = {
        "Total Games": "total_games",
        "Win Rate": "win_rate",
        "Avg Kill %": "avg_kill_dmg",
        "Avg Death %": "avg_death_dmg",
        "Avg Damage Per Opening": "avg_dpo",
        "Avg Damage Per Game": "avg_damage",
        "Avg Opening Conversion Rate": "avg_ocr",
        "Avg Openings Per Kill": "avg_opk",
        "Avg Game Time": "avg_time"
        }

    #Widgets
    timeSlider = DateSlider(start=df["matchStartTime"].min(), end=df["matchStartTime"].max(), value = df["matchStartTime"].min())
    selAxis_player = Select(title="Player Graph Statistic", options=list(axis_map_player.keys()), value="Total Games")

    source_player = ColumnDataSource(data=dict(x=[], 
                                               count=[] 
                                               #color=[]
                                               ))


    p_player = figure(height = 400, width = 800, tools="save", toolbar_location="right", title="Player Character Stats")
    p_player.vbar()
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

        source_player.data = dict(
            x=agg.index,
            counts=agg[player_axis]
            #color=
            )

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
tabs = Tabs(tabs=[("Overview", overview_tab(df))])

curdoc().add_root(tabs)
curdoc().title = "Data Visualizer"

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