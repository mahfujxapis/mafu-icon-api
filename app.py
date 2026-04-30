from flask import Flask, request, jsonify, send_file
import json
import os
import requests
from io import BytesIO
from PIL import Image

app = Flask(__name__)

DATA_FILE = "Itemdata.json"
VALID_KEY = "MAFU"  # Sirf yeh key accept hogi


def load_items():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("JSON Load Error:", e)
        return []


def verify_key():
    """Check if key is valid"""
    key = request.args.get("key")
    if not key or key != VALID_KEY:
        return False
    return True


@app.route("/")
def home():
    return {"status": "API running"}


# ITEM INFO API
@app.route("/info", methods=["GET"])
def get_item_info():
    # Key verification
    if not verify_key():
        return jsonify({"error": "Invalid or missing key 🔑"}), 401
    
    item_id = request.args.get("item_id")

    if not item_id:
        return jsonify({"error": "item_id required"}), 400

    try:
        item_id = int(item_id)
    except:
        return jsonify({"error": "item_id must be number"}), 400

    items = load_items()

    for item in items:
        if item.get("itemID") == item_id:
            return jsonify(item)

    return jsonify({"error": "Item not found"}), 404


# ICON API
@app.route("/icon", methods=["GET"])
def get_item_icon():
    # Key verification
    if not verify_key():
        return jsonify({"error": "Invalid or missing key 🔑"}), 401
    
    item_id = request.args.get("item_id")

    if not item_id:
        return jsonify({"error": "item_id required"}), 400

    try:
        item_id = int(item_id)
    except:
        return jsonify({"error": "item_id must be number"}), 400

    items = load_items()

    item = next((i for i in items if i.get("itemID") == item_id), None)

    if not item or not item.get("icon"):
        return jsonify({"error": "Item or icon not found"}), 404

    icon_name = item["icon"]

    image_url = f"https://freefiremobile-a.akamaihd.net/common/Local/PK/FF_UI_Icon/{icon_name}.png"

    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Icon image not found"}), 404

        img = Image.open(BytesIO(response.content))
        img_io = BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5019, debug=True)
