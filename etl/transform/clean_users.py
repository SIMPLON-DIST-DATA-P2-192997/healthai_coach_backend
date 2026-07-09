import pandas as pd
from faker import Faker
from datetime import datetime

fake = Faker("en")

def clean_users_activity():

    df_activity = pd.read_csv("etl/data/activity.csv", sep=",")
    df_user = pd.read_csv("etl/data/user.csv", sep=",")
    dfusers = pd.concat([df_activity, df_user], ignore_index=True) 
    
    # pour la table workout_session
    workout_session = dfusers[['Max_BPM', 'Avg_BPM']].copy()
    workout_session['started_at'] = pd.Timestamp.now()
    duration =  pd.to_timedelta(dfusers["Session_Duration (hours)"], unit = "h")
    workout_session["ended_at"] = workout_session["started_at"] + duration
    
    # pour la table biometric measurments
    dfusers = dfusers.drop("Unnamed: 0", axis=1)
    dfusers["Max_BPM"] = pd.to_numeric(dfusers["Max_BPM"], errors="coerce").astype("float64")
    col_string = dfusers.select_dtypes(include="string").columns
    dfusers[col_string] = dfusers[col_string].fillna("None")
    dfusers["source"] = "kaggle_gym_members"
    biometric_measurments = dfusers[['Weight (kg)', 'Height (m)', 'Resting_BPM', 'Fat_Percentage', "source"]].copy()
    
    # pour la table users 
    nouvelles_lignes = []
    
    for index, row in dfusers.iterrows():
        
        Faker.seed(index) 
        
        nouvel_utilisateur = {
           
            "Age": row.get("Age"),
            "sex": row.get("Gender"),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "hashed_password": "fake_hashed_password"
        }
        
        nouvelles_lignes.append(nouvel_utilisateur) 
    users = pd.DataFrame(nouvelles_lignes)
    users["sex"] = users["sex"].replace({"Male":"M", "Female": "F", "None" : "Other"})
    return users, biometric_measurments, workout_session
