import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry
import json

DATA_PATH = "./etl/data"

kaggle_datasets = [
  {
    'name': "nutrition.csv",
    'url': "https://www.kaggle.com/api/v1/datasets/download/adilshamim8/daily-food-and-nutrition-dataset"
  },
  {
    'name': "diet.csv",
    'url': "https://www.kaggle.com/api/v1/datasets/download/ziya07/diet-recommendations-dataset"
  },
  {
    'name': 'user.csv',
    'url': "https://www.kaggle.com/api/v1/datasets/download/valakhorasani/gym-members-exercise-dataset"
  },
  {
    'name': "activity.csv",
    'url': "https://www.kaggle.com/api/v1/datasets/download/nadeemajeedch/fitness-tracker-dataset"
  }
]


for item in kaggle_datasets:
  df = pd.read_csv(item['url'], compression='zip', on_bad_lines='skip')
  complete_path = DATA_PATH + "/" + item['name']
  
  df.to_csv(complete_path)
  


response = requests.get("https://oss.exercisedb.dev/api/v1/exercises?limit=25")
data = response.json() 

exercises = data['data']
hasNextPage = data['meta']['hasNextPage']
nextCursor = data['meta']['nextCursor']

@sleep_and_retry
@limits(calls=1, period=1) 
def fetch_data(cursor):
    url = f"https://oss.exercisedb.dev/api/v1/exercises?limit=25&after={cursor}"
    res = requests.get(url)
    
    if res.status_code == 200:
        return res.json()
    else:
        print(f"\n[!] L'API a bloqué. Code HTTP: {res.status_code}")
        return None

while hasNextPage:
    print(f"Récupération de la page suivante (curseur: {nextCursor})...")
    
    new_data = fetch_data(nextCursor)
    
    if new_data:
        exercises.extend(new_data['data'])

        hasNextPage = new_data['meta']['hasNextPage']
        nextCursor = new_data['meta']['nextCursor']
    else:
        print("Erreur lors de la récupération, arrêt de la boucle.")
        break

with open("./etl/data/exercicesAPI.json", mode='w', encoding="utf-8") as file:
  json.dump(exercises, file, indent=4, ensure_ascii=False)
  

# response_exercise_2 = requests.get('https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json')

# data = response_exercise_2.json()

# with open("./etl/data/exercices2.json", mode='w', encoding="utf-8") as file:
#   json.dump(data, file, indent=4, ensure_ascii=False)
  