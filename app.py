from flask import Flask, render_template, jsonify
import pymongo
from selenium_script import fetch_twitter_trends  # Import the Selenium script

app = Flask(__name__)

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["twitter_trends"]
collection = db["trending_topics"]

@app.route("/")
def home():
    # Fetch the most recent record from MongoDB to display
    latest_record = collection.find_one(sort=[("date_time", -1)])
    return render_template("index.html", record=latest_record)

@app.route("/run-script", methods=["GET"])
def run_script():
    # Run the Selenium script
    result = fetch_twitter_trends()
    if result:
        # Return the updated data to the template
        return render_template("index.html", record=result)
    else:
        return render_template("index.html", error="Failed to fetch trends. Please try again.")

if __name__ == "__main__":
    app.run(debug=True)
