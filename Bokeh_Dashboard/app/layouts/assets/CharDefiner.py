import pandas as pd

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


        