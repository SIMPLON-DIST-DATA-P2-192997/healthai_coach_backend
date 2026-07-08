import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open

from etl.transform.clean_diet import clean_diet
from etl.transform.clean_exercises import clean_exercices
from etl.transform.clean_nutrition import clean_nutrition
from etl.transform.clean_users import clean_users

# TEST : clean_diet

@patch('pandas.read_csv')
def test_clean_diet(mock_read_csv):
    mock_df = pd.DataFrame({
        "Unnamed: 0": [0, 1],
        "Aliment": ["Pomme", pd.NA],
        "Calories": [50, 100]
    })
    mock_df["Aliment"] = mock_df["Aliment"].astype("string")
    mock_read_csv.return_value = mock_df

    result = clean_diet()

    mock_read_csv.assert_called_once_with("etl/data/diet.csv", sep=",")
    assert "Unnamed: 0" not in result.columns
    assert result["Aliment"].iloc[1] == "None" 

# TEST : clean_exercices

@patch('json.load')
@patch('builtins.open', new_callable=mock_open)
def test_clean_exercices(mock_file, mock_json_load):
    mock_data = [{
        "bodyParts": ["chest", "arms"],
        "equipments": ["dumbbell", "barbell"],
        "targetMuscles": ["pecs"],
        "instructions": ["Step 1", "Step 2"]
    }]
    mock_json_load.return_value = mock_data

    result = clean_exercices()

    mock_file.assert_called_once_with("etl/data/exercicesAPI.json", "r", encoding="utf-8")
    assert result["bodyParts"].iloc[0] == "chest arms"
    assert result["equipments"].iloc[0] == "dumbbell barbell"
    assert result["targetMuscles"].iloc[0] == "pecs"
    assert result["instructions"].iloc[0] == "Step 1\nStep 2"


# TEST : clean_nutrition

@patch('pandas.read_csv')
def test_clean_nutrition(mock_read_csv):
    mock_df = pd.DataFrame({
        "Unnamed: 0": [0, 1],
        "Nutrient": ["Protéine", "Glucide"]
    })
    mock_read_csv.return_value = mock_df

    result = clean_nutrition()


    mock_read_csv.assert_called_once_with("etl/data/nutrition.csv", sep=",")
    assert "Unnamed: 0" not in result.columns
    assert "Nutrient" in result.columns
    assert len(result) == 2

# TEST : clean_users

@patch('pandas.read_csv')
def test_clean_users(mock_read_csv):
    df_activity = pd.DataFrame({
        "Unnamed: 0": [0],
        "Activity_ID": [1],
        "Max_BPM": ["150"], 
        "Type": ["Running"]
    }).astype({"Type": "string"})

    df_user = pd.DataFrame({
        "Unnamed: 0": [1],
        "User_ID": [100],
        "Max_BPM": ["Invalide_String"],
        "Name": [pd.NA] 
    }).astype({"Name": "string"})

    mock_read_csv.side_effect = [df_activity, df_user]

    result = clean_users()

    assert mock_read_csv.call_count == 2
    assert "Unnamed: 0" not in result.columns
    assert len(result) == 2 

    assert result["Max_BPM"].dtype == "float64"
    assert result["Max_BPM"].iloc[0] == 150.0
    assert np.isnan(result["Max_BPM"].iloc[1])

    assert result["Name"].iloc[1] == "None"