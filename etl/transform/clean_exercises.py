import json
import pandas as pd

def clean_exercises():
    with open("etl/data/exercicesAPI.json", "r", encoding="utf-8") as j:
        data = json.load(j)
        df_exercices = pd.DataFrame(data)
        cols = ["bodyParts", "equipments", "targetMuscles"]
        for col in cols:
            df_exercices[col] = df_exercices[col].apply(" ".join)
        df_exercices["instructions"] = df_exercices["instructions"].apply("\n".join)
        df_exercices["source"] = "exercisedb"
        exercises = df_exercices[['exerciseId', 'source', 'name', 'bodyParts',
       'targetMuscles', 'equipments', 'gifUrl', 'instructions']].copy()
        exercises.columns = ["external_id",'source', 'name', 'body_part', 'target_muscle', 'equipment', 'gif_url','instructions' ]
        return exercises