from bokeh.io import curdoc
from bokeh.models.widgets import Tabs, Panel
from layouts.overview_tab import overview_tab
from layouts.matchup_tab import matchup_tab
from layouts.timeseries_tab import timeseries_tab
from utils.data_loader import load_data

# --- Receive file path from PyQt ---
args = curdoc().session_context.request.arguments
file_path = args.get("file")[0].decode()

df = load_data(file_path)

# --- Build main tabs ---
overview = Panel(child=overview_tab(df), title="Overview")
characterMatchup = Panel(child=matchup_tab(df), title="Char & Match Up")
timeSeries = Panel(child=timeseries_tab(df), title="Time Series")

tabs = Tabs(tabs=[overview, characterMatchup, timeSeries])

curdoc().add_root(tabs)
curdoc().title = "Data Visualizer"