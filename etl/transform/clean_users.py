import pandas as pd

def clean_users():
    df_activity = pd.read_csv("etl/data/activity.csv", sep =",")
    df_user = pd.read_csv("etl/data/user.csv", sep =",")
    df_users = pd.concat([df_activity,df_user])
    df_users = df_users.drop("Unnamed: 0", axis=1)
    df_users["Max_BPM"] = pd.to_numeric(df_users["Max_BPM"], errors="coerce").astype("float64")
    col_string = df_users.select_dtypes(include="string").columns
    df_users[col_string] = df_users[col_string].fillna("None")
    return df_users
