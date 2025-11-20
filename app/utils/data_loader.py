import json

def load_json(path): #loads the dictionary pulled from the Javascript
    
    def replace_none(x): #for ease of math operations I want the None's to be nan's
        if x is None:
            return float('nan')
        if isinstance(x, list):
            return [replace_none(v) for v in x]
        if isinstance(x, dict):
            return {k: replace_none(v) for k, v in x.items()}
        return x
    
    with open(path, "r") as f:
        data = json.load(f)
    
    return replace_none(data)

