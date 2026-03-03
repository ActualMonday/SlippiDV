import os
import base64
from bokeh.layouts import column, row, layout
from bokeh.models import ColumnDataSource, Select, Slider, FactorRange, Range1d, Div, TextAreaInput, DateRangeSlider, RadioButtonGroup, Whisker
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure
import pandas as pd
from bokeh.io import curdoc
import numpy as np

#used in assigning name and color to stageID
def StageBar(xs):
    stageMap = {
        "other": "other",
        "2": "Fountain of Dreams",
        "3": "Stadium",
        "8": "Yoshi's Story",
        "28": "Dream Land N64",
        "31": "Battlefield",
        "32": "Final Destination"
        }

    colorMap = {
        "other": "other",
        "2": "#b384fa",
        "3": "#43a956",
        "8": "#b3d8f5",
        "28": "#e1b574",
        "31": "#e9d25d",
        "32": "#fe00fe"
        }

    stageList = [stageMap[i] for i in xs]
    colorList = [colorMap[i] for i in xs]
    return stageList, colorList

def png_to_base64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

def matchup_tab(df, done_signal):
    
    sliderSize = 600
    subSliderSize = 300
    plotHeight = 450

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

    axis_map_stage = {
        "Win Rate": "win_rate",
        "Avg Kill %": "avg_kill_dmg",
        "Avg Death %": "avg_death_dmg",
        "Avg Damage Per Opening": "avg_dpo",
        "Avg Damage Per Game": "avg_damage",
        "Avg Opening Conversion Rate": "avg_ocr",
        "Avg Openings Per Kill": "avg_opk",
        "Avg Neutral Win Rate": "avg_nwr",
        "Avg Game Time (s)": "avg_time"
        }

    axis_map_stage_sem = {
        "Win Rate": "win_rate_sem",
        "Avg Kill %": "avg_kill_dmg_sem",
        "Avg Death %": "avg_death_dmg_sem",
        "Avg Damage Per Opening": "avg_dpo_sem",
        "Avg Damage Per Game": "avg_damage_sem",
        "Avg Opening Conversion Rate": "avg_ocr_sem",
        "Avg Openings Per Kill": "avg_opk_sem",
        "Avg Neutral Win Rate": "avg_nwr_sem",
        "Avg Game Time (s)": "avg_time_sem"
        }
    #Widgets
    dateSelectSlider = DateRangeSlider(start=df["matchStartTime"].min().to_pydatetime(), end=df["matchStartTime"].max().to_pydatetime(), value = (df["matchStartTime"].min().to_pydatetime(), df["matchStartTime"].max().to_pydatetime()), title="Select Between Dates", width=sliderSize)
    selAxis_stage = Select(title="Stage Graph Statistic", options=list(axis_map_stage.keys()), value="Win Rate", width=sliderSize)
    minGamesSlider = Slider(start=0, end=50, value = 0, title="Mininum Played Games (Data Cut Off; only applied to time-series plot and table)", width=sliderSize)

    playerCharSelect = Select(title="Player Character", options=list(CharacterSelect.keys()), value="All")
    oppCharSelect = Select(title="Opponent Character", options=list(CharacterSelect.keys()), value="All")
    oppConnCodeFilter = TextAreaInput(title="Opponent Connection Code", value="", rows = 3)

    confidenceIntButtons= RadioButtonGroup(name="Confidence Interval", labels = ["Off", "68%", "95%", "99.7%"], active=0, width=sliderSize)
    

    #textboxes
    textConfInt = Div(text="<bf>Confidence Intervals Toggle</bf>")
    textDescriptConfInt = Div(text="These options above are here to test statistical signficance! <br> 'Off' = average value of your selected game statistic.<br> Confidence Intervals = the range where your average would lie X% of the time if you were to play the same number of games at current skill. <br><br> These were calculated assuming normal (bell curve) distributions. While usually appropriate, it is obviously not possible for your win rate to exceed 1, so feel to analyze with nuance. <br><br> These stats may also vary significantly dependent on who you're playing. :)", width =sliderSize)
    textConnCode = Div(text="Got a rival, or need to know where to take your bracket's Foxes? <br> Filter by your opponent/s connect code with a ',' between each for multiple. <br><br> Example: <br>FOX1#123,FOX2#613,PHAI#591")
    errUser = Div(text="")
    errOpp = Div(text="")
    statBox = Div(text="", width = sliderSize)
    br = Div(text="<br>", width= sliderSize)
    tableText = Div(text="Turn up the minimum games slider to filter these 1 game win rates!", width=sliderSize)
    


    TOOLTIPS_stage = [
    ("Statistic", "@stat"),
    ("Games Played", "@games")
    ]

    TOOLTIPS_time = [
    ("Statistic", "@y"),
    ("Date Range", "@date"),
    ("Games Played", "@games"),
    ("Most Played Opponent", "@opp")
    ]

    #initiate stage sources
    source_stage = ColumnDataSource(data=dict(x=[], 
                                               counts=[],
                                               stat=[],
                                               games=[],
                                               color=[]
                                               ))
    source_stage_icons = ColumnDataSource(data=dict(x=[], 
                                               y=[],
                                               icons=[]
                                               ))

    source_time = ColumnDataSource(data=dict(x=[], 
                                               y=[],
                                               date=[],
                                               games=[],
                                               opp=[]
                                               ))

    source_time_text = ColumnDataSource(data=dict(x=[], 
                                               y=[],
                                               text=[]
                                               ))

    source_CI = ColumnDataSource(data=dict(x=[],
                                           semlo=[],
                                           semhi=[]
                                           ))

    #Create Plots
    p_stage = figure(height = 700, width = 800, x_range=FactorRange(), y_range=Range1d(), tools="save,undo,redo,box_zoom", tooltips=TOOLTIPS_stage, toolbar_location="right", title="Sorted By Stage", output_backend="webgl")
    p_stage.vbar(x="x", top="counts", color="color", width=0.9, source=source_stage)
    error_renderer = p_stage.segment(x0='x', y0='semlo', x1='x', y1='semhi', line_color="white", line_width=2, line_cap='butt', source=source_CI)
    #error_renderer = p_stage.add_layout((base='x', lower='semlo', upper='semhi', line_color="white", line_width=2, capsize=10, source=source_CI))
    p_stage.image_url(url='icons', x='x', y='y', w=40, h=40, w_units="screen", h_units="screen", anchor="bottom_center", source=source_stage_icons)
    p_stage.xaxis.axis_label = "Stage"

    p_time = figure(height = 200, width = 800, x_range=Range1d(), toolbar_location="right", tools="save,crosshair,reset", tooltips=TOOLTIPS_time, title="Statistic Binned Over Time (hover for detials)", output_backend="canvas", x_axis_type="datetime")
    p_time.line(x='x', y='y', line_width=2, color = "#FEBE3F", line_alpha = 0.33, source=source_time)
    p_time.circle(x='x', y='y', fill_color = "white", line_color="black", size=8, source=source_time)
    p_time.xaxis.axis_label = "Time (s)"
    timeErrText = p_time.text(x="x", y="y", text="text",source=source_time_text)
    #############################
    #       ICONS AAAAA         #
    #############################

    # Preload all icons as Base64
    stages=[2,3,8,28,31,32,"other"]
    #static_folder = "C:/Users/Hugh Sharp/Documents/GitHub/SlippiDV/SlippiDVFinal/static/" #Will need to change!
    static_folder = "static/" #Will need to change!
    icons_base64 = [png_to_base64(os.path.join(static_folder, f"Stage/{i}.png")) for i in stages] #for stages
    

    #structure I had before worked for characters  and icons since they were numberedd 0-25
    #since these numbers don't have order I need to map there order INCLUDING my 'other'
    #Feels stupid way to fix this lolol

    iconMap = {
        "2": 0,
        "3": 1,
        "8": 2,
        "28": 3,
        "31": 4,
        "32": 5,
        "other": 6
        }

    charIconDict = {}
    
    for i in list(CharacterSelect.values()):
        charIconDict[i] = png_to_base64("static/Character/"+i+".png")
    
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

    def StatBoxUpdate(df_old):

        agg_stat = df_old.groupby("oppConnCode").agg(
            total_games=("oppConnCode", "size"),
            win_rate=("matchResult", "mean")
            )

        agg_stat["oppCode"] = agg_stat.index
        

        agg_stat = selected_by_stat(agg_stat)
        

        #make rows
        mostPlayed = agg_stat.loc[agg_stat["total_games"].idxmax()]
        bestWR = agg_stat.loc[agg_stat["win_rate"].idxmax()]
        worstWR = agg_stat.loc[agg_stat["win_rate"].idxmin()]

        
        stats = {
            "": ["Connection Code", "Win Rate", "Total Games"],
            "Most Played": [mostPlayed["oppCode"], str(mostPlayed["win_rate"])[0:5], mostPlayed["total_games"]],
            "Best Win Rate": [bestWR["oppCode"], str(bestWR["win_rate"])[0:5], bestWR["total_games"]],
            "Worst Win Rate": [worstWR["oppCode"], str(worstWR["win_rate"])[0:5], worstWR["total_games"]],
            }

        

        # Build rows for the table
        rows = []
        for category, values in stats.items():
            label = category
            rows.append([label] + list(values))

        #print(rows)

        # Convert to HTML
        table_html = """
        <table style="
            width:100%;
            table-layout: fixed;
            border-collapse: collapse;
            font-size:14px;">
        """

        for r in rows:
            table_html += "<tr>"
            for cell in r:
                table_html += f"""
                <td style="
                    border:1px solid #ccc;
                    padding:6px 10px;
                    text-align:center;">
                    {cell}
                </td>
                """
            table_html += "</tr>"

        table_html += "</table>"

        statBox.text = table_html

    #Define what data is currently displayed (i.e. selected)
    def selected_by_game():
        # Convert slider float (ms since epoch) to a pandas Timestamp
        slider_starttime = pd.to_datetime(dateSelectSlider.value[0], unit="ms", utc=True)
        slider_endtime = pd.to_datetime(dateSelectSlider.value[1], unit="ms", utc=True)
        # Filter the DataFrame
        #selected = df[df["matchStartTime"] >= slider_starttime & df["matchStartTime"] <= slider_endtime]
        selected = df[(df["matchStartTime"] >= slider_starttime) & (df["matchStartTime"] <= slider_endtime)]

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
        userCharPlayed = df_old['oppChar'].unique().tolist()

        oppCharID_now = CharacterSelect[oppCharSelect.value]

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
                
    def time_bin_average(df_old, time_col, num_bins):
        # 1) boundaries
        tmin = df_old[time_col].min()
        tmax = df_old[time_col].max()
        bins = pd.date_range(start=tmin, end=tmax, periods=num_bins+1)

        # 2) categorize
        df_old = df_old.copy() #this seems unessecary...
        #print(len(df_old[time_col]))
        #print(df_old[time_col])
        if len(df_old[time_col]) != 1:

            df_old["time_bin"] = pd.cut(df_old[time_col], bins=bins)
        
            #3) aggregate
            agg_time = df_old.groupby("time_bin").agg(
            avg_date=("matchStartTime", "mean"),
            total_games=("time_bin", "size"),
            win_rate=("matchResult", "mean"),
            avg_kill_dmg=("userDPS", "mean"),
            avg_death_dmg=("oppDPS", "mean"),
            avg_dpo=("userDPO", "mean"),
            avg_damage=("userDmg", "mean"),
            avg_nwr=("userNWR", "mean"),
            avg_opk=("userOPK", "mean"),
            avg_ocr=("userOCR", "mean"),
            avg_time=("gameTime", "mean"),
            most_opp=("oppConnCode", lambda x: x.mode().iloc[0] if not x.mode().empty else None)
            ).dropna()

            #print(agg_time)

            return agg_time

        else:
            #3) aggregate
            row1 = df_old.iloc[0]
            t = row1["matchStartTime"]

            single_interval = pd.Interval(left=t, right=t, closed="both")

            agg_time = pd.DataFrame(
                {
                    "avg_date":      [t],
                    "total_games":   [1],
                    "win_rate":      [row1["matchResult"]],
                    "avg_kill_dmg":  [row1["userDPS"]],
                    "avg_death_dmg": [row1["oppDPS"]],
                    "avg_dpo":       [row1["userDPO"]],
                    "avg_damage":    [row1["userDmg"]],
                    "avg_nwr":       [row1["userNWR"]],
                    "avg_opk":       [row1["userOPK"]],
                    "avg_ocr":       [row1["userOCR"]],
                    "avg_time":      [row1["gameTime"]],
                    "most_opp":      [row1["oppConnCode"]],
                },
                index=pd.IntervalIndex([single_interval], name="time_bin"),
            )

            #print(agg_time)
            return agg_time

    def selected_by_stat(agg_old):
        
        agg_selected = agg_old[agg_old['total_games'] > minGamesSlider.value] 
                               

        return agg_selected

    hide_loading_js = CustomJS(code="""
        const el = document.getElementById("loading-overlay");
        if (el) el.style.display = "none";
    """)

    curdoc().add_next_tick_callback(
        lambda: hide_loading_js
    )

    def update():

        #loading_div.text = loading_div.text.replace("none", "flex")

        #define new df filtering by game properties
        df_selected = selected_by_game()

        #Stage Sorted Data
        stage_axis = axis_map_stage[selAxis_stage.value]
        sem_axis = axis_map_stage_sem[selAxis_stage.value]
        p_stage.yaxis.axis_label = selAxis_stage.value

        #set up err_txt for booleon
        err_txt = ""

        df_selected, err_txt = UserCharFilt(df_selected)

        if err_txt == "":
            errUser.text = err_txt
            df_selected, err_txt = OppCharFilt(df_selected, oppConnCodeFilter.value)
            errOpp.text = err_txt
        else:
            errUser.text = err_txt
            errOpp.text = ""

        
        #Identify illegal stages in df
        legalStages = [2, 3, 8, 28, 31, 32]

        illegal_stage_mask = ~df_selected['stage'].isin(legalStages)

        df_selected.loc[illegal_stage_mask, 'stage'] = 'other'

        StatBoxUpdate(df_selected)

        #aggregate stats
        agg = df_selected.groupby("stage").agg(
        total_games=("userChar", "size"),
        win_rate=("matchResult", "mean"),
        avg_kill_dmg=("userDPS", "mean"),
        avg_death_dmg=("oppDPS", "mean"),
        avg_dpo=("userDPO", "mean"),
        avg_damage=("userDmg", "mean"),
        avg_nwr=("userNWR", "mean"),
        avg_opk=("userOPK", "mean"),
        avg_ocr=("userOCR", "mean"),
        avg_time=("gameTime", "mean"),
        win_rate_sem=("matchResult", "sem"),
        avg_kill_dmg_sem=("userDPS", "sem"),
        avg_death_dmg_sem=("oppDPS", "sem"),
        avg_dpo_sem=("userDPO", "sem"),
        avg_damage_sem=("userDmg", "sem"),
        avg_nwr_sem=("userNWR", "sem"),
        avg_opk_sem=("userOPK", "sem"),
        avg_ocr_sem=("userOCR", "sem"),
        avg_time_sem=("gameTime", "sem"))

        

        #define new df filtering by statistic properties
        #agg = selected_by_stat(agg) #min games slider

        agg = agg.sort_values(by=stage_axis, ascending = False)

        #grab final lists
        xs = agg.index.astype(str).tolist()
        count = agg[stage_axis].tolist()
        chars, colors = StageBar(xs)
        iconlist = [icons_base64[iconMap[c]] for c in xs]
        sem = agg[sem_axis].tolist()

        if confidenceIntButtons.active == 3:
            semlo = [count[i] - sem[i]*3 for i, dumbyvar in enumerate(count)]
            semhi = [count[i] + sem[i]*3 for i, dumbyvar in enumerate(count)]
            error_renderer.visible = True
            #alph = 1
        elif confidenceIntButtons.active == 2:
            semlo = [count[i] - sem[i]*2 for i, dumbyvar in enumerate(count)]
            semhi = [count[i] + sem[i]*2 for i, dumbyvar in enumerate(count)]
            error_renderer.visible = True
            #alph = 1
        elif confidenceIntButtons.active == 1:
            semlo = [count[i] - sem[i] for i, dumbyvar in enumerate(count)]
            semhi = [count[i] + sem[i] for i, dumbyvar in enumerate(count)]
            error_renderer.visible = True
            #alph = 1
        else:
            semlo = count
            semhi = count
            error_renderer.visible = False
            #alph = 0

        #print(sem)

        #update sources
        source_stage.data = dict(
            x=chars,
            counts=count,
            stat=count,
            games=agg["total_games"].tolist(),
            color=colors
            )
        
        source_stage_icons.data = dict(
            x=chars,
            y=[i + 0.05*max(count) for i in count],
            icons=iconlist
            )

        source_CI.data = dict(
            x=chars,
            semlo=semlo,
            semhi=semhi
            )

        p_stage.x_range.factors = chars
        p_stage.y_range.end = max(count)*1.25

        #standard error


        #time series plot
        #bin
        p_time.yaxis.axis_label = selAxis_stage.value

        df_timeBin = time_bin_average(df_selected, "matchStartTime", 300)
        
        #define new df filtering by statistic properties
        
        startDate=pd.to_datetime(dateSelectSlider.value[0], unit="ms", utc=True)
        endDate=pd.to_datetime(dateSelectSlider.value[1], unit="ms", utc=True)

        midDate = startDate + (endDate-startDate)/2

        interval_list = [i.left.strftime('%m/%d/%Y') + "-" + i.right.strftime('%m/%d/%Y') for i in df_timeBin.index.to_list()]


        if df_timeBin.loc[df_timeBin["total_games"].idxmax()]["total_games"] < minGamesSlider.value: #Bug occurs when min game slider is greater than any of the binned times, but smaller than total games played still showing in statbox
            
            y_time = df_timeBin[stage_axis].tolist()

            source_time.data = dict(
                x=[midDate],
                y=[np.mean(y_time)]
                )
            source_time_text = dict(
                x=[midDate],
                y=[np.mean(y_time) * 1.1],
                text=["Displaying Average; Min. Games Slider > games played in single session (bin)"]
                )
        else:
            df_timeBin = selected_by_stat(df_timeBin)

            y_time = df_timeBin[stage_axis].tolist()

            source_time.data = dict(
                x=df_timeBin["avg_date"].tolist(),
                y=y_time,
                date=interval_list,
                games=df_timeBin["total_games"].to_list(),
                opp=df_timeBin["most_opp"].to_list()
                )
            source_time_text = dict(
                x=[midDate],
                y=[np.mean(y_time) * 1.1],
                text=[""]
                )
        p_time.x_range.start = startDate
        p_time.x_range.end = endDate

        """
        y_time = agg_time[stage_axis].tolist()

        source_time.data = dict(
            x=agg.index.tolist(),
            y=y_time
            )
        """
        done_signal.text = str(int(done_signal.text) + 1)
        #loading_div.text = loading_div.text.replace("flex", "none")

    
    #Make loading screen appear
    

    show_loading_js = CustomJS(code="""
        const el = document.getElementById("loading-overlay");
        if (el) el.style.display = "flex";
    """)

    #controls = [DateSlider minGamesSlider, selAxis_player, selAxis_opp, selChar_opp]

    #Make Controls
    dateSelectSlider.on_change('value_throttled', lambda attr, old, new: update())
    minGamesSlider.on_change('value_throttled', lambda attr, old, new: update())
    selAxis_stage.on_change('value', lambda attr, old, new: update())
    confidenceIntButtons.on_change('active', lambda attr, old, new: update())

    playerCharSelect.on_change('value', lambda attr, old, new: update())
    oppCharSelect.on_change('value', lambda attr, old, new: update())
    oppConnCodeFilter.on_change('value', lambda attr, old, new: update())

    #Update Loading Screen (Comment out if loading screen feels extra)
    dateSelectSlider.js_on_change('value_throttled', show_loading_js)
    minGamesSlider.js_on_change('value_throttled', show_loading_js)
    selAxis_stage.js_on_change('value', show_loading_js)
    confidenceIntButtons.js_on_change('active', show_loading_js)

    playerCharSelect.js_on_change('value', show_loading_js)
    oppCharSelect.js_on_change('value', show_loading_js)
    oppConnCodeFilter.js_on_change('value', show_loading_js)

    #controls1 = [dateSelectSlider, selAxis_stage, playerCharSelect]
    #controls2 = [oppCharSelect]
    #controls3 = [oppConnCodeFilter]

    #Make column for inputs
    #inputs = column(*controls1, errUser, *controls2, errOpp, *controls3, textConnCode, width=sliderSize, sizing_mode="fixed")

    controls1 = [dateSelectSlider, selAxis_stage, minGamesSlider]
    controls2 = [playerCharSelect]
    controls3 = [oppCharSelect, oppConnCodeFilter]
    controls4 = [confidenceIntButtons]

    inputs = column(*controls1, row(column(*controls2, errUser, row(userImgBox, vsImgBox, oppImgBox), width=subSliderSize, sizing_mode="fixed"), column(*controls3, errOpp, textConnCode, width=subSliderSize, sizing_mode="fixed")), textConfInt, *controls4, textDescriptConfInt, br, statBox, tableText, width=sliderSize, sizing_mode="fixed")
    #Make column for plots
    plots = column(p_stage, p_time, width=1000, sizing_mode="stretch_width")

    update()  # initial load of the data
    

    layout = row(
    plots,
    inputs,
    sizing_mode="stretch_width",
    width_policy="max"
    )

    return layout