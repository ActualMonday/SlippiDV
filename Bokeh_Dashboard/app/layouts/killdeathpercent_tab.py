import os
import base64
from bokeh.layouts import column, row, layout
from bokeh.models import ColumnDataSource, Select, RangeSlider, Range1d, Div, TextAreaInput, DateRangeSlider, RadioButtonGroup, Span, HoverTool, Label
from bokeh.plotting import figure
import pandas as pd
from bokeh.io import curdoc
import numpy as np
from bokeh.transform import cumsum
from bokeh.models.callbacks import CustomJS

def png_to_base64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

def killdeathpercent_tab(df, done_signal):

    sliderSize = 600
    subSliderSize = 300
    subsubSize = 100

    #used for error msgs
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

    #used for filters
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

    #stage filter
    stageMap = {
        "All": "All",
        "Fountain of Dreams": "2",
        "Stadium": "3",
        "Yoshi's Story": "8",
        "Dream Land N64": "28",
        "Battlefield": "31",
        "Final Destination": "32" 
        }

    moveMap = {
        0:  "None",
        1:  "Misc.",
        2:  "Jab 1",
        3:  "Jab 2",
        4:  "Jab 3",
        5:  "Rapid Jabs",
        6:  "Dash Attack",
        7:  "Ftilt",
        8:  "Utilt",
        9:  "Dtilt",
        10:  "Fsmash",
        11: "Usmash",
        12: "Dsmash",
        13: "Nair",
        14: "Fair",
        15: "Bair",
        16: "Uair",
        17: "Dair",
        18: "Neutral B",
        19: "Side B",
        20: "Up B",
        21: "Down B",
        50: "Getup Attack",
        51: "Getup Attack (Slow)",
        52: "Pummel",
        53: "F-throw",
        54: "B-throw",
        55: "U-throw",
        56: "D-throw",
        61: "Edge Attack (Slow)",
        62: "Edge Attack"
        }

    #Widgets
    dateSelectSlider = DateRangeSlider(start=df["matchStartTime"].min().to_pydatetime(), end=df["matchStartTime"].max().to_pydatetime(), value = (df["matchStartTime"].min().to_pydatetime(), df["matchStartTime"].max().to_pydatetime()), title="Select Between Dates", width=sliderSize)
    xaxisSlider = RangeSlider(start=0, end=250, value=(0, 250), title = "%-Range Displayed", width=sliderSize)
    selStage = Select(title="Select Stage", options=list(stageMap.keys()), value = 'All', width = sliderSize)
    killDeathButtons = RadioButtonGroup(labels=["Kills", "Deaths"], active=0, width=sliderSize)

    playerCharSelect = Select(title="Player Character", options=list(CharacterSelect.keys()), value="All")
    oppCharSelect = Select(title="Opponent Character", options=list(CharacterSelect.keys()), value="All")
    oppConnCodeFilter = TextAreaInput(title="Opponent Connection Code", value="", rows = 3)

    #textboxes
    textConnCode = Div(text="Need to know what to fish for against your rival? <br> Filter by your opponent/s connect code with a ',' between each for multiple. <br><br> Example: <br>FOX1#123,FOX2#613,PHAI#591")
    errUser = Div(text="")
    errOpp = Div(text="")
    killDeathText = Div(text="Toggle move statistics by your kill moves / moves that kill you!", width = sliderSize)
    stageText = Div(text="""<div style="text-align: right;"><h1>Stage:</h1></div>""", width = subsubSize)
    percentText = Div(text="""<div style="text-align: left;">Can use <a href="https://ikneedata.com/calculator.html">https://ikneedata.com/calculator.html</a> by Schmoo and GentleFox to calculate typical kill % thresholds for greater context.</div>""", width = 800)

    #sources
    source_hist1 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist2 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist3 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist4 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist5 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist6 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist7 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist8 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist9 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist10 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist11 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    source_hist12 = ColumnDataSource(data=dict(
        counts=[],
        left=[],
        right=[]
        ))
    
    

    #create plots
    p_hist1 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist1.quad(top="counts", bottom=0, left="left", right="right", source=source_hist1, fill_color = "#6565FE")
    span1 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist1.add_layout(span1)
    hover1 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist1.add_tools(hover1)
    label1 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist1.add_layout(label1)
    

    p_hist2 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist2.quad(top="counts", bottom=0, left="left", right="right", source=source_hist2, fill_color = "#6565FE")
    span2 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist2.add_layout(span2)
    hover2 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist2.add_tools(hover2)
    label2 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist2.add_layout(label2)
    

    p_hist3 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist3.quad(top="counts", bottom=0, left="left", right="right", source=source_hist3, fill_color = "#6565FE")
    span3 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist3.add_layout(span3)
    hover3 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist3.add_tools(hover3)
    label3 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist3.add_layout(label3)

    p_hist4 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist4.quad(top="counts", bottom=0, left="left", right="right", source=source_hist4, fill_color = "#6565FE")
    span4 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist4.add_layout(span4)
    hover4 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist4.add_tools(hover4)
    label4 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist4.add_layout(label4)
    

    p_hist5 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist5.quad(top="counts", bottom=0, left="left", right="right", source=source_hist5, fill_color = "#6565FE")
    span5 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist5.add_layout(span5)
    hover5 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist5.add_tools(hover5)
    label5 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist5.add_layout(label5)
    

    p_hist6 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist6.quad(top="counts", bottom=0, left="left", right="right", source=source_hist6, fill_color = "#6565FE")
    span6 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist6.add_layout(span6)
    hover6 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist6.add_tools(hover6)
    label6 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist6.add_layout(label6)
    

    p_hist7 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist7.quad(top="counts", bottom=0, left="left", right="right", source=source_hist7, fill_color = "#6565FE")
    span7 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist7.add_layout(span7)
    hover7 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist7.add_tools(hover7)
    label7 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist7.add_layout(label7)
    

    p_hist8 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist8.quad(top="counts", bottom=0, left="left", right="right", source=source_hist8, fill_color = "#6565FE")
    span8 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist8.add_layout(span8)
    hover8 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist8.add_tools(hover8)
    label8 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist8.add_layout(label8)
    

    p_hist9 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist9.quad(top="counts", bottom=0, left="left", right="right", source=source_hist9, fill_color = "#6565FE")
    span9 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist9.add_layout(span9)
    hover9 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist9.add_tools(hover9)
    label9 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist9.add_layout(label9)
    

    p_hist10 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist10.quad(top="counts", bottom=0, left="left", right="right", source=source_hist10, fill_color = "#6565FE")
    span10 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist10.add_layout(span10)
    hover10 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist10.add_tools(hover10)
    label10 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist10.add_layout(label10)


    p_hist11 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist11.quad(top="counts", bottom=0, left="left", right="right", source=source_hist11, fill_color = "#6565FE")
    span11 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist11.add_layout(span11)
    hover11 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist11.add_tools(hover11)
    label11 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist11.add_layout(label11)


    p_hist12 = figure(height = 300, width = 300, tools="save,crosshair", x_range=Range1d(), toolbar_location="right", title="", output_backend="webgl")
    p_hist12.quad(top="counts", bottom=0, left="left", right="right", source=source_hist12, fill_color = "#6565FE")
    span12 = Span(location=0, dimension = 'height', line_color='#FEBE3F', line_width=3)
    p_hist12.add_layout(span12)
    hover12 = HoverTool(
        tooltips=[('%', "$x")],
        attachment="horizontal",
        mode='vline'
        )
    p_hist12.add_tools(hover12)
    label12 = Label(x=100, y=100, x_units="screen", y_units="screen", text='No data! Go play more! >:)', text_color = "white", text_align="center", render_mode='canvas')
    p_hist12.add_layout(label12)


    #Pie Chart! 
    source_pie = ColumnDataSource(data=dict(
        move=[],
        angle=[],
        color=[],
        counts=[],
        perc=[]
        ))

    TOOLTIPS_pie = [
        ("Move", "@move"),
        ("Count", "@counts"),
        ("% of Total", "@perc")
    ]

    # hehe "p sub pie" <3
    p_pie = figure(height = 400, width = sliderSize, title="", toolbar_location=None, tooltips = TOOLTIPS_pie, x_range=(-0.5, 1.0), output_backend="webgl")
    p_pie.wedge(x=0,y=1,radius=0.4, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'), fill_color="color", legend_field = "move", line_alpha=0, source=source_pie)
    p_pie.axis.axis_label = None
    p_pie.axis.visible = False
    p_pie.grid.grid_line_color = None
    p_pie.background_fill_color = None

    p_pie.outline_line_color = None  
    #p_pie.min_border = 10       # gives layout something to hold on to
    #p_pie.width = 500
    #p_pie.height = 500

    #p_pie.min_border_right = 300   # adjust as needed

    hover = HoverTool(
        tooltips=TOOLTIPS_pie,
        renderers=[p_pie.renderers[-1]]
        )

    p_pie.add_tools(hover)
    """
    #Make multi-column legend
    items = [
        LegendItem(label=move, renderers=[wedge], index=i)
        for i, move in enumerate(source_pie.data["move"])
    ]

    # Split into 3 columns
    col_size = (len(items) + 2) // 3   # ceiling divide
    col1 = items[:col_size]
    col2 = items[col_size:2*col_size]
    col3 = items[2*col_size:]

    legend1 = Legend(items=col1, location="center")
    legend2 = Legend(items=col2, location="center")
    legend3 = Legend(items=col3, location="center")

    # Put legends on the right side in a row
    p_pie.add_layout(legend1, 'right')
    p_pie.add_layout(legend2, 'right')
    p_pie.add_layout(legend3, 'right')
    p_pie.legend.location = "center_right"
    p_pie.legend.orientation = "vertical"

    # Let Bokeh compute its own layout more safely
    p_pie.legend.spacing = 5
    p_pie.legend.padding = 5
    p_pie.legend.margin = 0
    """

    #melee_ui colors
    pie_colors = [
    "#39FF14",  # neon green
    "#00E5FF",  # electric cyan
    "#FF6EC7",  # neon pink
    "#7DF9FF",  # laser blue
    "#FFEA00",  # highlighter yellow
    "#FF1493",  # deep magenta
    "#00FF9F",  # bright aqua green
    "#FF5F1F",  # neon orange
    "#993CFF",  # vivid purple
    "#3CFFB5",  # mint neon

    # 10–17: ULTRA-NEON + highly distinct
    "#FF66FF",  # cotton-candy neon
    "#FF00F7",  # hot magenta
    "#FF3131",  # pure neon red
    "#FF7A00",  # glowing orange
    "#9D00FF",  # neon violet
    "#00B3FF",  # neon sky blue
    "#FFFC00",  # blinding yellow
    "#00FF3C",  # bright green

    "#00FFD1",  # bright turquoise
    "#66FF66",  # soft neon green
    "#66B3FF",  # cool neon blue
    "#FFB366",  # warm neon peach
    "#B366FF",  # lavender neon
    "#66FFF2",  # pastel teal neon
    "#FF668C",  # retro pink-red
    "#33CCFF",  # light electric blue
    "#CC33FF",  # retro purple
    "#FFCC33",  # golden neon
    "#33FF66",  # greenish neon
    "#FF33A8",   # punchy pink
    "#3CD9FF"
]
    
    colorMap = {}
    listMoves = list(moveMap.keys())
    for i in range(0, len(listMoves)):
        colorMap[listMoves[i]] = pie_colors[i]
    # Preload all icons as Base64
    stages=[2,3,8,28,31,32,"All"]
    #static_folder = "C:/Users/Hugh Sharp/Documents/GitHub/SlippiDV/SlippiDVFinal/static/" #Will need to change!
    static_folder = "static/" #Will need to change!
    

    charIconDict = {}
    stageIconDict = {}

    for i in list(CharacterSelect.values()):
        charIconDict[i] = png_to_base64("static/Character/"+i+".png")
    
    for i in stages:
        stageIconDict[str(i)] = png_to_base64("static/Stage/"+str(i)+".png")

    userImgBox = Div(text=f"""
        <div style='padding:9px;'>
            <img src={charIconDict["All"]} style="width:75px;">
        </div>
    """)

    vsIcon = png_to_base64("static/vs.png")
    vsImgBox = Div(text=f"""
        <div style='padding:9px;'>
            <img src={vsIcon} style="width:75px;">
        </div>
    """)
    
    oppImgBox = Div(text=f"""
        <div style='padding:9px;'>
            <img src={charIconDict["All"]} style="width:75px;">
        </div>
    """)

    stageImgBox = Div(text=f"""
        <div style='padding:9px;'>
            <img src={stageIconDict["All"]} style="width:75px;">
        </div>
    """)

    def ImgBoxUpdate(player, id):
        if player == "user":
            userImgBox.text = f"""
            <div style='padding:9px;'>
                <img src={charIconDict[id]} style="width:75px;">
            </div>
            """
        else:
            oppImgBox.text = f"""
            <div style='padding:9px;'>
                <img src={charIconDict[id]} style="width:75px;">
            </div>
            """

    def StageImgUpdate(id):
        stageImgBox.text=f"""
            <div style='padding:9px;'>
                <img src={stageIconDict[id]} style="width:75px;">
            </div>
            """

    def selected_by_game():
        # Convert slider float (ms since epoch) to a pandas Timestamp
        slider_starttime = pd.to_datetime(dateSelectSlider.value[0], unit="ms", utc=True)
        slider_endtime = pd.to_datetime(dateSelectSlider.value[1], unit="ms", utc=True)
        # Filter the DataFrame
        #selected = df[df["matchStartTime"] >= slider_starttime & df["matchStartTime"] <= slider_endtime]

        if selStage.value != "All":
            selected = df[(df["matchStartTime"] >= slider_starttime) & (df["matchStartTime"] <= slider_endtime) & (df["stage"] == int(stageMap[selStage.value]))]
        else:
            selected = df[(df["matchStartTime"] >= slider_starttime) & (df["matchStartTime"] <= slider_endtime)]

        StageImgUpdate(stageMap[selStage.value])

        return selected

    def UserCharFilt(df_old): #returns error statement if filtering by a character you haven't played
        #Current bugs:
        #Doesn't recognize any games upon filtering
        #displays correct character in error message

        userCharPlayed = df_old['userChar'].unique().tolist()

        #print(userCharPlayed)

        userCharID_now = CharacterSelect[playerCharSelect.value]

        if userCharID_now == "All":
            #print(df_old)
            ImgBoxUpdate('user','All')
            return df_old, ''
        elif int(userCharID_now) not in userCharPlayed: #you don't play this character
            #print(df_old)
            ImgBoxUpdate('user','All')
            ImgBoxUpdate('opp','All')
            return df_old, 'ERROR: Currently NO games filtered by your '+ charMap[userCharID_now] +'. <br> Displaying stats for all player/opp characters.'
        else:
            df_new = df_old[df_old["userChar"] == int(userCharID_now)]
            #print(df_old[df_old["userChar"] == charID_now])
            #print(df_new == df_old)
            ImgBoxUpdate('user',userCharID_now)
            return df_new, ''

    def OppCharFilt(df_old, connCodes): #returns error statement if filtering by a character you haven't played
        #Current bugs: 
        #Crashes upon opp filtering
        #Works fine on Connection Code filtering

        oppCharPlayed = df_old['oppChar'].unique().tolist()

        oppCharID_now = CharacterSelect[oppCharSelect.value]
        userCharID_now = CharacterSelect[playerCharSelect.value]

        oppCharName = oppCharSelect.value
        userCharName = playerCharSelect.value

        if connCodes == '': #no connection codes listed

            if oppCharID_now == "All": #happy
                ImgBoxUpdate('opp',oppCharID_now)
                return df_old, ''
            elif int(oppCharID_now) not in oppCharPlayed: #your character hasn't played vs their character
                ImgBoxUpdate('opp',"All")
                return df_old, 'ERROR: NO games versus '+ oppCharName +' as your '+ oppCharName +' within selected time-interval. <br> Displaying stats for all opponent characters.'
            else: #happy
                df_old = df_old[df_old["oppChar"] == int(oppCharID_now)]
                ImgBoxUpdate('opp',oppCharID_now)
                return df_old, ''

        else:
            connCodesList = [p.strip() for p in connCodes.split(",")]

            if all([df_old['oppConnCode'].isin([i]).any() for i in connCodesList]): #checks if valid conn codes
                
                df_old = df_old[df_old['oppConnCode'].isin(connCodesList)]
                oppCharPlayed = df_old['oppChar'].unique().tolist()

                if oppCharID_now == "All": #happy
                    ImgBoxUpdate('opp',oppCharID_now)
                    return df_old, ''
                elif int(oppCharID_now) not in oppCharPlayed: #you have played these people but not in this match up
                    ImgBoxUpdate('opp',"All")
                    return df_old, 'ERROR: These connection codes DID NOT play this character (' + oppCharName + ') versus your selected character (' + userCharName + ') in selected time-interval. <br> <br> Displaying ALL games against connection codes versus your' + userCharName + '.'
                else: #happy
                    df_old = df_old[df_old["oppChar"] == int(oppCharID_now)]
                    ImgBoxUpdate('opp',oppCharID_now)
                    return df_old, ''

            else: #invalid connection codes

                if oppCharID_now == "All": #Invalid connection code
                    ImgBoxUpdate('opp',oppCharID_now)
                    return df_old, 'ERROR: Atleast 1 connection code is either; <br> 1) Invalid/Incorrect. <br> 2) Not found in database over selected time-interval. <br><br> Displaying ALL games against your ' + userCharName + '.'
                elif int(oppCharID_now) not in oppCharPlayed: #Invalid connection code AND not played the match up 
                    ImgBoxUpdate('opp',"All")
                    return df_old, 'ERROR: Atleast 1 connection code is either; <br> 1) Invalid/Incorrect. <br> 2) Not found in database over selected time-interval. <br><br> ERROR: You also have not played the match up '+ oppCharName +' versus your '+ userCharName +' in selected time-interval. Displaying ALL games against your '+ userCharName +'.'
                else: #Invalid connection code, but you have played the match up
                    df_old = df_old[df_old["oppChar"] == int(oppCharID_now)]
                    ImgBoxUpdate('opp',oppCharID_now)
                    return df_old, 'ERROR: Atleast 1 connection code is either; <br> 1) Invalid/Incorrect. <br> 2) Not found in database over selected time-interval. <br><br> Displaying ALL games of '+ oppCharName +' versus '+ userCharName +'.'
    
    def HistUpdate(agg_, p_hist, source, span, label, moveID): #agg, figure, data source, span, line for label, and move to histogram

        #print(moveID)

        if moveID == None:
            source.data = dict(
                counts=[0],
                left=[0],
                right=[1]
                )

            label.visible = True
            

            p_hist.x_range.start = xaxisSlider.value[0]
            p_hist.x_range.end = xaxisSlider.value[1]
            span.visible = False

            if killDeathButtons.active == 0:
                p_hist.title.text = "N/A"
                p_hist.title.align = "center"
                p_hist.yaxis.axis_label = "Kills"
                p_hist.xaxis.axis_label = "Kill % (after hit)"
            else:
                p_hist.title.text = f"N/A"
                p_hist.title.align = "center"
                p_hist.yaxis.axis_label = "Deaths"
                p_hist.xaxis.axis_label = "Death % (after hit)"
        else:
            label.visible = False

            killPercents = np.asarray(agg_.loc[moveID, "killPercents"])
        
            bins = np.arange(0, max(killPercents)+ 5, 5)
            counts, edges = np.histogram(killPercents, bins=bins)

        
            source.data = dict(
                counts=counts,
                left=edges[:-1],
                right=edges[1:]
                )
            """
            source_text.data = dict(
                textx=[np.mean([xaxisSlider.value[0], xaxisSlider.value[1]])],
                texty=[0.5*max(killPercents)],
                right=["testing"]
                )
                """
            
            move = moveMap[moveID]
            kills = str(len(killPercents))
            percent = str(int(np.mean(killPercents)))

        
            p_hist.x_range.start = xaxisSlider.value[0]
            p_hist.x_range.end = xaxisSlider.value[1]
            span.location = np.mean(killPercents)
            span.visible = True

            if killDeathButtons.active == 0:
                p_hist.title.text = f"{move}: {kills} Total Kills,   Avg = {percent}%"
                p_hist.title.align = "center"
                p_hist.yaxis.axis_label = "Kills"
                p_hist.xaxis.axis_label = "Kill % (after hit)"
            else:
                p_hist.title.text = f"{move}: {kills} Total Deaths,  Avg = {percent}%"
                p_hist.title.align = "center"
                p_hist.yaxis.axis_label = "Deaths"
                p_hist.xaxis.axis_label = "Death % (after hit)"

        
    """      
    def update_xdisplay(event): #update function for the hover crosshair
        x_label1.x = event.x
        x_label1.y = p_hist1.y_range.end  # put label at top of plot
        x_label1.text = f"x = {event.x:.2f}%"
    """

    def update():

        #loading_div.text = loading_div.text.replace("none", "flex")

        #define new df filtering by game properties
        df_selected = selected_by_game()

        err_txt = ""

        df_selected, err_txt = UserCharFilt(df_selected)

        if err_txt == "":
            errUser.text = err_txt
            df_selected, err_txt = OppCharFilt(df_selected, oppConnCodeFilter.value)
            errOpp.text = err_txt
        else:
            errUser.text = err_txt
            errOpp.text = ""
        
        if killDeathButtons.active == 0:
            moveToggle = "userKillInfo"
        else:
            moveToggle = "oppKillInfo"

        Kills = {
            "killMoves": sum((d["killMoves"] for d in df_selected[moveToggle]), []),
            "killPercents": sum((d["killPercents"] for d in df_selected[moveToggle]), [])
            }
        df_Kills = pd.DataFrame(Kills)
        

        agg = df_Kills.groupby("killMoves").agg(list)
        
        agg = agg[agg.index.isin(list(moveMap.keys()))] #ensures only moves in "moveMap" are registered

        
        #ordering kill moves from most kills to least kills
        orderOfKillMoves = agg["killPercents"].str.len().sort_values(ascending = False).index.tolist()

        #if there aren't enough moves for plots, I'll append 'None' till there are atleast 12 indices in orderOfKillMoves
        while len(orderOfKillMoves) < 12:
            orderOfKillMoves.append(None)

        
        HistUpdate(agg, p_hist1, source_hist1, span1, label1, orderOfKillMoves[0]) #agg, figure, data source, span, line for label, and move to histogram
        HistUpdate(agg, p_hist2, source_hist2, span2, label2, orderOfKillMoves[1])
        HistUpdate(agg, p_hist3, source_hist3, span3, label3, orderOfKillMoves[2])
        HistUpdate(agg, p_hist4, source_hist4, span4, label4, orderOfKillMoves[3])
        HistUpdate(agg, p_hist5, source_hist5, span5, label5, orderOfKillMoves[4])
        HistUpdate(agg, p_hist6, source_hist6, span6, label6, orderOfKillMoves[5])
        HistUpdate(agg, p_hist7, source_hist7, span7, label7, orderOfKillMoves[6])
        HistUpdate(agg, p_hist8, source_hist8, span8, label8, orderOfKillMoves[7])
        HistUpdate(agg, p_hist9, source_hist9, span9, label9, orderOfKillMoves[8])
        HistUpdate(agg, p_hist10, source_hist10, span10, label10, orderOfKillMoves[9])
        HistUpdate(agg, p_hist11, source_hist11, span11, label11, orderOfKillMoves[10])
        HistUpdate(agg, p_hist12, source_hist12, span12, label12, orderOfKillMoves[11])
        
        #piechart (filter by xaxisSlider)
        agg['killPercents'] = agg['killPercents'].apply(lambda x: [num for num in x if xaxisSlider.value[0] <= num <= xaxisSlider.value[1]])

        orderOfKillMoves = agg["killPercents"].str.len().sort_values(ascending = False).index.tolist() #Recalculate for pi chart (also will get rid of Nones!)

        killsTotal = agg["killPercents"].apply(len).sum()
        move = [moveMap[int(i)] for i in orderOfKillMoves]
        counts = [len(agg.loc[i, "killPercents"]) for i in orderOfKillMoves]
        angle = [i/killsTotal * 2*np.pi for i in counts] 
        color = [colorMap[int(i)] for i in orderOfKillMoves]
        perc = [str(i/killsTotal * 100)[0:4] + "%" for i in counts]

        source_pie.data = dict(
            move=move,
            angle=angle,
            color=color,
            counts=counts,
            perc=perc
        )
        
        if killDeathButtons.active == 0:
            p_pie.title.text = "Total Kills Between " + str(xaxisSlider.value[0]) + "-" + str(xaxisSlider.value[1]) +"%: " + str(killsTotal) + " (hover for details)"
        else:
            p_pie.title.text = "Total Deaths Between " + str(xaxisSlider.value[0]) + "-" + str(xaxisSlider.value[1]) +"%: " + str(killsTotal) + " (hover for details)"

        #loading_div.text = loading_div.text.replace("flex", "none")
        done_signal.text = str(int(done_signal.text) + 1)
    
    #Make loading screen appear
    show_loading_js = CustomJS(code="""
        const el = document.getElementById("loading-overlay");
        if (el) el.style.display = "flex";
    """)
    

    #Update Data
    dateSelectSlider.on_change('value_throttled', lambda attr, old, new: update())
    xaxisSlider.on_change('value_throttled', lambda attr, old, new: update())
    selStage.on_change('value', lambda attr, old, new: update())
    killDeathButtons.on_change('active', lambda attr, old, new: update())

    playerCharSelect.on_change('value', lambda attr, old, new: update())
    oppCharSelect.on_change('value', lambda attr, old, new: update())
    oppConnCodeFilter.on_change('value', lambda attr, old, new: update())

    #Update Loading Screen (comment out if loading screen feels extra)
    dateSelectSlider.js_on_change('value_throttled', show_loading_js)
    xaxisSlider.js_on_change('value_throttled', show_loading_js)
    selStage.js_on_change('value', show_loading_js)
    killDeathButtons.js_on_change('active', show_loading_js)

    playerCharSelect.js_on_change('value', show_loading_js)
    oppCharSelect.js_on_change('value', show_loading_js)
    oppConnCodeFilter.js_on_change('value', show_loading_js)
    

    #p_hist1.on_event("mousemove", update_xdisplay)

    controls1 = [dateSelectSlider, xaxisSlider, selStage]
    controls4 = [killDeathButtons]
    controls2 = [playerCharSelect]
    controls3 = [oppCharSelect, oppConnCodeFilter]

    inputs = column(*controls1, killDeathText, *controls4, row(column(*controls2, errUser, row(userImgBox, vsImgBox, oppImgBox), row(stageText, stageImgBox), width=subSliderSize, sizing_mode="fixed"), column(*controls3, errOpp, textConnCode, width=subSliderSize, sizing_mode="fixed")), p_pie, width=sliderSize, sizing_mode="fixed")
    plots = column(row(p_hist1,p_hist2,p_hist3,p_hist4, sizing_mode="stretch_width"),row(p_hist5,p_hist6,p_hist7,p_hist8, sizing_mode="stretch_width"),row(p_hist9,p_hist10,p_hist11,p_hist12, sizing_mode="stretch_width"), percentText, width=1000, sizing_mode="stretch_width")

    update()  # initial load of the data


    layout = row(
    plots,
    inputs,
    sizing_mode="stretch_width",
    width_policy="max"
    )

    return layout