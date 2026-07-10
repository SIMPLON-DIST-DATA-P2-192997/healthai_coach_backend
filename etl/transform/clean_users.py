import random
from datetime import datetime
import pandas as pd
from faker import Faker

fake = Faker("en")
fake.seed_instance(42)


def clean_users_activity() -> pd.DataFrame:
    df_activity = pd.read_csv("etl/data/activity.csv", sep=",")
    df_user = pd.read_csv("etl/data/user.csv", sep=",")
    dfusers = pd.concat([df_activity, df_user], ignore_index=True)

    workout_session = dfusers[["Max_BPM", "Avg_BPM"]].copy()
    workout_session["started_at"] = pd.Timestamp.now()
    duration = pd.to_timedelta(dfusers["Session_Duration (hours)"], unit="h")
    workout_session["ended_at"] = workout_session["started_at"] + duration

    col_string = dfusers.select_dtypes(include="string").columns
    if len(col_string) > 0:
        dfusers[col_string] = dfusers[col_string].fillna("None")

    dfusers["source"] = "kaggle_gym_members"
    biometric_measurments = dfusers[
        ["Weight (kg)", "Height (m)", "Resting_BPM", "Fat_Percentage", "source"]
    ].copy()
    biometric_measurments.columns = [
        "Weight",
        "Height",
        "Resting_BPM",
        "Fat_Percentage",
        "source",
    ]

    nouvelles_lignes = []
    current_year = datetime.now().year

    for index, row in dfusers.iterrows():
        age = row.get("Age")

        random.seed(index)

        nouvel_utilisateur = {
            "date_of_birth": (
                f"{current_year - int(age)}-{random.randint(1,12):02}-{random.randint(1,28):02}"
                if pd.notna(age)
                else "2000-01-01"
            ),
            "sex": row.get("Gender"),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "hashed_password": "seed-not-a-real-hash",
        }

        nouvelles_lignes.append(nouvel_utilisateur)

    users = pd.DataFrame(nouvelles_lignes)
    users["sex"] = users["sex"].replace(
        {"Male": "M", "Female": "F", "None": "other"}
    )

    df_concat = pd.concat(
        [users, biometric_measurments, workout_session], axis=1
    )
    df_concat = df_concat.dropna(subset=["ended_at"])

    df_concat["Max_BPM"] = (
        pd.to_numeric(df_concat["Max_BPM"], errors="coerce")
        .astype("Int64")
    )
    df_concat["Resting_BPM"] = df_concat["Resting_BPM"].astype("Int64")
    df_concat["Avg_BPM"] = df_concat["Avg_BPM"].astype("Int64")

    return df_concat


if __name__ == "__main__":
    r = clean_users_activity()
    print("Aperçu du dataset propre :")
    print(r.head())