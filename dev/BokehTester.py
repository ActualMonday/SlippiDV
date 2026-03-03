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