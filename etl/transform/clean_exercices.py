import json
import pandas as pd

def clean_exercices():
    with open("etl/data/exercicesAPI.json", "r", encoding="utf-8") as j:
        data = json.load(j)
        df_exerices = pd.DataFrame(data)
        cols = ["bodyParts", "equipments", "targetMuscles"]
        for col in cols:
            df_exerices[col] = df_exerices[col].apply("".join)
        return df_exerices
