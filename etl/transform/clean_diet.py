import pandas as pd

def clean_diet():
    df_diet = pd.read_csv("etl/data/diet.csv", sep =",")

    df_diet = df_diet.drop("Unnamed: 0", axis=1)
    col_string = df_diet.select_dtypes(include="string").columns
    df_diet[col_string] = df_diet[col_string].fillna("None")
    return df_diet

