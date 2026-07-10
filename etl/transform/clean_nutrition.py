import pandas as pd 

def clean_nutrition():
    df_nutrition = pd.read_csv("etl/data/nutrition.csv", sep =",")
    df_nutrition["source"] = "kaggle_daily_food_nutrition"
    df_food_items = df_nutrition[['Unnamed: 0', 'source', 'Food_Item', 'Category', 'Calories (kcal)', 'Protein (g)','Carbohydrates (g)', 'Fat (g)', 'Fiber (g)', 'Sugars (g)','Sodium (mg)', 'Cholesterol (mg)']].copy()
    df_food_items.columns = ["external_id",'source', "name", "category", "calories_kcal", "protein_g", "carbs_g","fat_g", "fiber_g","sugar_g", "sodium_mg", "cholesterol_mg"]
    return df_food_items


    
