from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, Slider, DateSlider
from bokeh.plotting import figure
import pandas as pd
from collections import Counter

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
    timeSlider = DateSlider(start=df["matchStartTime"].min(), end=df["matchStartTime"].max(), value = df["matchStartTime"].min)
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
        [inputs, p],
    ], sizing_mode="scale_both")

    return l
        