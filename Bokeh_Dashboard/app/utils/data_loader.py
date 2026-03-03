import json
from json import tool
from re import T
from tkinter import SEL
import numpy as np
import pandas as pd

def load_data(path):

    def replace_none(x): #for ease of math operations I want the None's to be nan's
        if x is None:
            return float('nan')
        if isinstance(x, list):
            return [replace_none(v) for v in x]
        if isinstance(x, dict):
            return {k: replace_none(v) for k, v in x.items()}
        return x

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        data = json.load(f)

    #column_data = columnize(data)
    rows_fin = pd.DataFrame(replace_none(data)) # need to make the matchTime into TimeStamp
    rows_fin["matchStartTime"] = pd.to_datetime(rows_fin["matchStartTime"], format="mixed", utc=True)

    return rows_fin


