from flask import Flask, render_template 
import pymongo
from bson import ObjectId
from selenium_script import fetch_twitter_trends
import datetime

app = Flask(__name__)

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["twitter_trends"]
collection = db["trending_topics"]

# Helper function to serialize MongoDB documents
def serialize_mongo_document(doc):
    if doc:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

@app.route("/")
def home():
    latest_record = collection.find_one(sort=[("timestamp", -1)])
    latest_record = serialize_mongo_document(latest_record)  # Serialize the document
    return render_template("index.html", record=latest_record)

@app.route("/run-script", methods=["GET"])
def run_script():
    try:
        result = fetch_twitter_trends()
        trending_topics = result.get("trends", [])
        proxy_used = result.get("proxy_used", "Unknown")

        if trending_topics:
            record = {
                "timestamp": datetime.datetime.now(),
                "trends": trending_topics,
                "proxy_used": proxy_used,
            }
            collection.insert_one(record)
            return home()
        else:
            return render_template("index.html", error="Failed to fetch trends.")

    except Exception as e:
        return render_template("index.html", error=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
