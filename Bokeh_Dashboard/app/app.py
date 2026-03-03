from bokeh.io import curdoc
from bokeh.models import Tabs, Panel, Div
from layouts.overview_tab import overview_tab
from layouts.matchup_tab import matchup_tab
from layouts.killdeathpercent_tab import killdeathpercent_tab
#from layouts.timeseries_tab import timeseries_tab
from utils.data_loader import load_data
from bokeh.models.callbacks import CustomJS


file_path = 'C:/Users/Hugh Sharp/Documents/GitHub/SlippiDV/SlippiDV_FullData.json' #test for now

df = load_data(file_path)

# --- Build main tabs ---
#overview = Panel(child=overview_tab(df), title="Overview")
#characterMatchup = Panel(child=matchup_tab(df), title="Char & Match Up")
#timeSeries = Panel(child=timeseries_tab(df), title="Time Series")

loading_div = Div(text="""
<div id="loading-overlay" style="
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.3);
    display: none;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: white;
    z-index: 9999;
    pointer-events: none;
">
    Loading...
</div>
""")

done_signal = Div(text="0", visible=False)

hide_loading_js = CustomJS(code="""
const el = document.getElementById("loading-overlay");
if (el) el.style.display = "none";
""")

done_signal.js_on_change("text", hide_loading_js)



tabs = Tabs(tabs=[
    Panel(child=overview_tab(df, done_signal), title="Overview"),
    Panel(child=matchup_tab(df, done_signal), title="Match Up"),
    Panel(child=killdeathpercent_tab(df, done_signal), title="Kill/Death %")
    #Panel(child=overview_tab(df), title="Overview"),
    #Panel(child=matchup_tab(df), title="Match Up"),
    #Panel(child=killdeathpercent_tab(df), title="Kill/Death %")
])

from bokeh.layouts import layout

curdoc().add_root(
    layout([
        tabs,
        loading_div  
    ])
)

curdoc().add_root(done_signal)

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
