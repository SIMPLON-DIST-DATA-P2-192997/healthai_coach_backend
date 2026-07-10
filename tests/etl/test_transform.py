from etl.transform.clean_diet import clean_diet
from etl.transform.clean_exercises import clean_exercises
from etl.transform.clean_nutrition import clean_nutrition
from etl.transform.clean_users import clean_users_activity


import pandas as pd
from unittest.mock import patch, mock_open
from datetime import timedelta

# TEST : clean_diet

@patch('pandas.read_csv')
def test_clean_diet(mock_read_csv):
    mock_df = pd.DataFrame({
        "Unnamed: 0": [0, 1],
        "Disease_Type": ["Type1", None],
        "Severity": ["High", "Low"],
        "Cholesterol_mg/dL": [200, 180],
        "Blood_Pressure_mmHg": ["120/80", "110/70"],
        "Glucose_mg/dL": [90, 85],
        "Dietary_Restrictions": ["Vegan", None],
        "Allergies": ["Peanuts", "None"],
        "Preferred_Cuisine": ["Italian", "French"]
    })
    mock_read_csv.return_value = mock_df

    df_med, df_diet = clean_diet()

    assert "Unnamed: 0" not in df_med.columns
    assert "Unnamed: 0" not in df_diet.columns
    assert df_med.loc[1, "Disease_Type"] == "None"
    assert df_diet.loc[1, "Dietary_Restrictions"] == "None"
    assert len(df_med.columns) == 5
    assert len(df_diet.columns) == 3

# TEST : clean_exercices

@patch('json.load')
@patch('builtins.open', new_callable=mock_open)
def test_clean_exercices(mock_file, mock_json_load):
    mock_data = [{
        "exerciseId": "001",
        "name": "Push up",
        "bodyParts": ["Chest", "Arms"],
        "targetMuscles": ["Pectorals"],
        "equipments": ["Body weight"],
        "gifUrl": "http://example.com/pushup.gif",
        "instructions": ["Step 1", "Step 2"]
    }]
    mock_json_load.return_value = mock_data

    df_exercises = clean_exercises()

    assert len(df_exercises) == 1
    assert df_exercises.loc[0, "body_part"] == "Chest Arms"
    assert df_exercises.loc[0, "instructions"] == "Step 1\nStep 2"
    assert df_exercises.loc[0, "source"] == "exercisedb"
    assert "external_id" in df_exercises.columns

# TEST : clean_nutrition

@patch('pandas.read_csv')
def test_clean_nutrition(mock_read_csv):
    mock_df = pd.DataFrame({
        "Unnamed: 0": [0],
        "Food_Item": ["Apple"],
        "Category": ["Fruit"],
        "Calories (kcal)": [52],
        "Protein (g)": [0.3],
        "Carbohydrates (g)": [14],
        "Fat (g)": [0.2],
        "Fiber (g)": [2.4],
        "Sugars (g)": [10],
        "Sodium (mg)": [1],
        "Cholesterol (mg)": [0]
    })
    mock_read_csv.return_value = mock_df

    df_nutrition = clean_nutrition()

    assert df_nutrition.loc[0, "source"] == "kaggle_daily_food_nutrition"
    assert "calories_kcal" in df_nutrition.columns
    assert df_nutrition.loc[0, "calories_kcal"] == 52
    assert len(df_nutrition.columns) == 12

# TEST : clean_users_activity

@patch('pandas.read_csv')
def test_clean_users_activity(mock_read_csv):
    mock_df_activity = pd.DataFrame({
        "Unnamed: 0": [0],
        "Max_BPM": ["180"],
        "Avg_BPM": [140],
        "Session_Duration (hours)": [1.5],
        "Weight (kg)": [75],
        "Height (m)": [1.80],
        "Resting_BPM": [60],
        "Fat_Percentage": [15]
    })

    mock_df_user = pd.DataFrame({
        "Unnamed: 0": [1],
        "Gender": ["Male"],
        "Session_Duration (hours)": [1.0],
        "Max_BPM": ["150"],
        "Avg_BPM": [120],
        "Weight (kg)": [80],
        "Height (m)": [1.75],
        "Resting_BPM": [55],
        "Fat_Percentage": [18],
    })

    mock_read_csv.side_effect = [mock_df_activity, mock_df_user]

    df = clean_users_activity()

    assert "started_at" in df.columns
    assert "ended_at" in df.columns
    delta = df.loc[0, "ended_at"] - df.loc[0, "started_at"]
    assert delta == timedelta(hours=1.5)

    assert df.loc[0, "source"] == "kaggle_gym_members"
    assert "Unnamed: 0" not in df.columns

    assert df.loc[1, "sex"] == "M"
    assert df.loc[1, "hashed_password"] == "seed-not-a-real-hash"
    assert isinstance(df.loc[1, "first_name"], str)