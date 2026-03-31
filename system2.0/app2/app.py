from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "analyzed_clusters.json")


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


data = load_data()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/data")
def get_all_data():
    return jsonify(data)


@app.route("/api/cluster/<int:cluster_id>")
def get_cluster(cluster_id):
    selected = next((item for item in data if item["cluster_id"] == cluster_id), None)

    if selected:
        return jsonify(selected)

    return jsonify({"error": "Cluster not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)