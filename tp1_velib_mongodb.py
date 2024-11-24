import requests
from pymongo import MongoClient
import time
import threading

# Configuration
API_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=20"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "VelibDB"
COLLECTION_NAME = "stations"
REFRESH_INTERVAL = 60  # Rafraîchissement des données (en secondes)

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Fonction pour récupérer les données depuis l'API
def fetch_velib_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        raw_data = response.json()
        return raw_data.get('records', [])
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données : {e}")
        return []

# Fonction pour nettoyer les données
def clean_data(raw_data):
    return [
        {
            "name": record['fields'].get('name', "Station inconnue"),
            "lat": record['fields'].get('coordonnees_geo', [0, 0])[0],
            "lon": record['fields'].get('coordonnees_geo', [0, 0])[1],
            "ebike": record['fields'].get('ebike', 0),
            "mechanical": record['fields'].get('mechanical', 0),
            "num_bikes_available": record['fields'].get('num_bikes_available', 0),
            "num_docks_available": record['fields'].get('num_docks_available', 0),
        }
        for record in raw_data
        if 'fields' in record and 'coordonnees_geo' in record['fields']
    ]

# Fonction pour insérer les données dans MongoDB
def insert_to_mongodb(data):
    try:
        collection.delete_many({})  # Supprimez les anciennes données
        collection.insert_many(data)  # Insérez les nouvelles données
        print("Données insérées avec succès dans MongoDB.")
    except Exception as e:
        print(f"Erreur lors de l'insertion dans MongoDB : {e}")

# Fonction pour rafraîchir les données toutes les minutes
def refresh_data():
    while True:
        print("Rafraîchissement des données...")
        raw_data = fetch_velib_data()
        cleaned_data = clean_data(raw_data)
        if cleaned_data:
            insert_to_mongodb(cleaned_data)
        time.sleep(REFRESH_INTERVAL)

# Lancement du rafraîchissement en arrière-plan
if __name__ == "__main__":
    threading.Thread(target=refresh_data, daemon=True).start()
    print("Rafraîchissement automatique des données en cours...")
