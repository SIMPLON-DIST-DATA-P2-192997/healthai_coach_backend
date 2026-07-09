import pandas as pd


def clean_diet():
    df_diet = pd.read_csv("etl/data/diet.csv", sep=",")
    df_diet = df_diet.drop("Unnamed: 0", axis=1)
   
    col_string = df_diet.select_dtypes(include=["object", "string"]).columns
    df_diet[col_string] = df_diet[col_string].fillna("None")
    
    # pour la table medical_profiles
    df_medical_profiles = df_diet[
        [
            "Disease_Type",
            "Severity",
            "Cholesterol_mg/dL",
            "Blood_Pressure_mmHg",
            "Glucose_mg/dL"
        ]
    ].copy()
    #table dietary_preferences 
    df_dietary_preferences = df_diet[
        [
            'Dietary_Restrictions', 'Allergies',
       'Preferred_Cuisine'
        ]
    ].copy()
    return df_medical_profiles, df_dietary_preferences


