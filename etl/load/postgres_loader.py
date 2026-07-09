# import psycopg2
# import os
# from psycopg2.extras import execute_batch
from sqlalchemy import create_engine
import pandas as pd
import os
from etl.transform.clean_nutrition import clean_nutrition
from etl.transform.clean_diet import clean_diet
from etl.transform.clean_exercises import clean_exercices
from etl.transform.clean_users import clean_users

medical_profile, dietary_preference = clean_diet()
exercises = clean_exercices()
food_items = clean_nutrition()
users, biometric_measurments, workout_sessions = clean_users()

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)
engine = create_engine(DATABASE_URL)

# DU DATAFRAME VERS SQL 
try:
    exercises.to_sql(
        name="exercises",
        con=engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )
    food_items.to_sql(
        name="food_items",
        con=engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )
except Exception as e:
    print(f"Error insertion : {e}")

