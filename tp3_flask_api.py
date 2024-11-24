from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "VelibDB"
COLLECTION_NAME = "stations"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

@app.route('/stations', methods=['GET'])
def get_stations():
    try:
        stations = list(collection.find({}, {'_id': 0}))
        return jsonify(stations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
