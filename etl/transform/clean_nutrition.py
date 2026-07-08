import pandas as pd 

def clean_nutrition():
    df_nutrition = pd.read_csv("etl/data/nutrition.csv", sep =",")
    df_nutrition = df_nutrition.drop("Unnamed: 0", axis=1)
    return df_nutrition
