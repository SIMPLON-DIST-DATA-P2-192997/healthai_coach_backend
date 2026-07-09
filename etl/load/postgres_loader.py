import psycopg2 
from sqlalchemy import create_engine
import sys
import os
import pandas as pd
from datetime import datetime

# Configuration du chemin de projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

# Imports de tes scripts de transformation
from etl.transform.clean_nutrition import clean_nutrition
from etl.transform.clean_diet import clean_diet
from etl.transform.clean_exercises import clean_exercises
from etl.transform.clean_users import clean_users_activity

print("🔄 Démarrage de la transformation des données...")
exercises = clean_exercises()
food_items = clean_nutrition()
medical_profile, dietary_preference = clean_diet()
user_infos = clean_users_activity()
print("✅ Transformation terminée.")

# Configuration de la base de données
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)
engine = create_engine(DATABASE_URL)
conn = psycopg2.connect(DATABASE_URL)

def safe_val(val):
    """Convertit les types nuls de Pandas (pd.NA, NaT, NaN) en None pour Postgres."""
    return None if pd.isna(val) else val

def load_exercises():
    print("⏳ Chargement de 'exercises' (UPSERT via table de staging)...")
    # 1. On charge le lot dans une table intermédiaire éphémère
    exercises.to_sql(
        name="staging_exercises",
        con=engine,
        if_exists='replace',
        index=False
    )
    
    # 2. On applique l'UPSERT natif de PostgreSQL
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO exercises 
                (external_id, source, name, body_part, target_muscle, equipment, gif_url, instructions)
            SELECT external_id, source, name, body_part, target_muscle, equipment, gif_url, instructions
            FROM staging_exercises
            ON CONFLICT (source, external_id) DO UPDATE SET
                name          = EXCLUDED.name,
                body_part     = EXCLUDED.body_part,
                target_muscle = EXCLUDED.target_muscle,
                equipment     = EXCLUDED.equipment,
                gif_url       = EXCLUDED.gif_url,
                instructions  = EXCLUDED.instructions,
                ingested_at   = NOW();
        """)
        cur.execute("DROP TABLE IF EXISTS staging_exercises;")
    conn.commit()
    
def load_food_items():
    print("⏳ Chargement de 'food_items' (UPSERT via table de staging)...")
    # 1. On charge dans la table de staging
    food_items.to_sql(
        name="staging_food_items",
        con=engine,
        if_exists='replace',
        index=False
    )
    
    # 2. On applique l'UPSERT natif
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO food_items 
                (external_id, source, name, category, calories_kcal, protein_g, carbs_g, fat_g, fiber_g, sugar_g, sodium_mg, cholesterol_mg)
            SELECT external_id, source, name, category, calories_kcal, protein_g, carbs_g, fat_g, fiber_g, sugar_g, sodium_mg, cholesterol_mg
            FROM staging_food_items
            ON CONFLICT (source, external_id) DO UPDATE SET
                name           = EXCLUDED.name,
                category       = EXCLUDED.category,
                calories_kcal  = EXCLUDED.calories_kcal,
                protein_g      = EXCLUDED.protein_g,
                carbs_g        = EXCLUDED.carbs_g,
                fat_g          = EXCLUDED.fat_g,
                fiber_g        = EXCLUDED.fiber_g,
                sugar_g        = EXCLUDED.sugar_g,
                sodium_mg      = EXCLUDED.sodium_mg,
                cholesterol_mg = EXCLUDED.cholesterol_mg,
                ingested_at    = NOW();
        """)
        cur.execute("DROP TABLE IF EXISTS staging_food_items;")
    conn.commit()
    
def load_users(cur):
    print("⏳ Chargement de 'users', 'biometric_measurements' et 'workout_sessions'...")
    generated_user_ids = []
    
    for index, row in user_infos.iterrows():
        # 1. Insertion ou Mise à jour de l'utilisateur sur conflit d'email (UPSERT)
        # RETURNING renvoie l'ID qu'il soit créé OU mis à jour, ce qui est parfait pour la suite.
        query = """
            INSERT INTO users
                (email, hashed_password, first_name, last_name, date_of_birth, sex)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                first_name    = EXCLUDED.first_name,
                last_name     = EXCLUDED.last_name,
                date_of_birth = EXCLUDED.date_of_birth,
                sex           = EXCLUDED.sex,
                updated_at    = NOW()
            RETURNING user_id;
            """
        cur.execute(query, (
            safe_val(row.email), safe_val(row.hashed_password), safe_val(row.first_name), 
            safe_val(row.last_name), safe_val(row.date_of_birth), safe_val(row.sex)
        ))
        generated_user_id = cur.fetchone()[0]
        generated_user_ids.append(generated_user_id)
        
        # 2. Table Biométrique (Donnée historique : on ajoute un nouveau relevé à chaque run)
        # Sécurité : Si un relevé existe déjà exactement à la même seconde, on ne fait rien
        query_biometrics = """
            INSERT INTO biometric_measurements
                (user_id, measured_at, weight_kg, height_cm, body_fat_pct, resting_heart_rate, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, measured_at) DO NOTHING;
        """
        cur.execute(query_biometrics, (
            generated_user_id, datetime.now(), safe_val(row.Weight), 
            safe_val(row.Height), safe_val(row.Fat_Percentage), safe_val(row.Resting_BPM), safe_val(row.source)
        ))
        
        # 3. Table des entraînements (Donnée historique : ajout continu)
        query_workout = """
            INSERT INTO workout_sessions
                (user_id, started_at, ended_at, max_bpm, avg_bpm)
            VALUES(%s, %s, %s, %s, %s)
        """
        cur.execute(query_workout, (
            generated_user_id, safe_val(row.started_at), safe_val(row.ended_at), 
            safe_val(row.Max_BPM), safe_val(row.Avg_BPM) 
        ))
        
    return generated_user_ids
    
def load_medical_profile(cur, id_list, df_medical):
    print("⏳ Chargement de 'medical_profiles'...")
    for user_id, (index, row) in zip(id_list, df_medical.iterrows()):
        query = """
            INSERT INTO medical_profiles
                (user_id, disease_type, severity, cholesterol_mg_dl, blood_pressure_mmhg, glucose_mg_dl, recorded_at)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            """
        cur.execute(query, (
            user_id, 
            safe_val(row['Disease_Type']), 
            safe_val(row['Severity']), 
            safe_val(row['Cholesterol_mg/dL']), 
            safe_val(row['Blood_Pressure_mmHg']), 
            safe_val(row['Glucose_mg/dL']),
            datetime.now()
        ))  
    
def load_dietary_preference(cur, id_list, df_dietary):
    print("⏳ Chargement de 'dietary_preferences'...")
    for user_id, (index, row) in zip(id_list, df_dietary.iterrows()):
        query = """
            INSERT INTO dietary_preferences
                (user_id, dietary_restrictions, allergies, preferred_cuisine)
            VALUES(%s, %s, %s, %s)
            """
        cur.execute(query, (
            user_id,
            safe_val(row['Dietary_Restrictions']),
            safe_val(row['Allergies']),
            safe_val(row['Preferred_Cuisine'])
        ))

def load_data():
    try:
        with conn:
            # PLUS DE TRUNCATE ICI : La base conserve son historique et ses relations
            with conn.cursor() as cur:
                load_exercises()
                load_food_items()
                
                id_list = load_users(cur)
                load_medical_profile(cur, id_list, medical_profile)
                load_dietary_preference(cur, id_list, dietary_preference)
                
            conn.commit()
            print("🚀 ===============================")
            print("🚀 Load OK : Pipeline Idempotent terminé avec succès !")
            print("🚀 ===============================")
            
    except Exception as e:
        print(f"❌ Erreur critique lors du chargement des données : {e}")
        conn.rollback() 
    finally:
        conn.close()

if __name__ == "__main__":
    load_data()