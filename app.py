from flask import Flask, request, jsonify
import hashlib
import difflib
import os

app = Flask(__name__)

# In-memory store
strings_data = {}

# ---------- Utility functions ----------
def check_length(value):
    return len(value)

def is_palindrome(value):
    cleaned = ''.join(ch.lower() for ch in value if ch.isalnum())
    return cleaned == cleaned[::-1]

def word_count(value):
    return len(value.split())

def unique_characters(value):
    return list(set(value))

def get_frequency(value):
    freq = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    return freq

def sha256_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def analyze_string(value):
    return {
        "string": value,
        "length": check_length(value),
        "is_palindrome": is_palindrome(value),
        "word_count": word_count(value),
        "unique_characters": unique_characters(value),
        "frequency": get_frequency(value),
        "sha256": sha256_hash(value),
    }


# ---------- 1️⃣ POST /strings ----------
@app.route("/strings", methods=["POST"])
def create_string():
    data = request.get_json(silent=True)

    if not data or "value" not in data:
        return jsonify({"error": "Missing 'value' field"}), 400

    value = data["value"]

    if not isinstance(value, str):
        return jsonify({"error": "Value must be a string"}), 422

    if value in strings_data:
        return jsonify({"error": "String already exists"}), 409

    result = analyze_string(value)
    strings_data[value] = result
    return jsonify(result), 201


# ---------- 2️⃣ GET /strings/<string_value> ----------
@app.route("/strings/<string_value>", methods=["GET"])
def get_string(string_value):
    result = strings_data.get(string_value)
    if not result:
        return jsonify({"error": "String not found"}), 404
    return jsonify(result), 200


# ---------- 3️⃣ GET /strings ----------
@app.route("/strings", methods=["GET"])
def get_all_strings():
    # No query params → return all
    if not request.args:
        return jsonify(list(strings_data.values())), 200

    filtered = list(strings_data.values())

    # Query filters
    if "is_palindrome" in request.args:
        val = request.args.get("is_palindrome").lower()
        if val not in ["true", "false"]:
            return jsonify({"error": "is_palindrome must be true or false"}), 422
        bool_val = val == "true"
        filtered = [s for s in filtered if s["is_palindrome"] == bool_val]

    if "length_gt" in request.args:
        try:
            limit = int(request.args.get("length_gt"))
            filtered = [s for s in filtered if s["length"] > limit]
        except ValueError:
            return jsonify({"error": "Invalid length_gt value"}), 422

    if "word_count" in request.args:
        try:
            count = int(request.args.get("word_count"))
            filtered = [s for s in filtered if s["word_count"] == count]
        except ValueError:
            return jsonify({"error": "Invalid word_count value"}), 422

    return jsonify(filtered), 200


# ---------- 4️⃣ GET /strings/filter-by-natural-language ----------
@app.route("/strings/filter-by-natural-language", methods=["GET"])
def filter_by_natural_language():
    """Example: ?query=palindrome or ?query=long"""
    query = request.args.get("query", "").lower()
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    results = []
    for s in strings_data.values():
        if ("palindrome" in query and s["is_palindrome"]) or \
           ("long" in query and s["length"] > 10) or \
           ("short" in query and s["length"] <= 5) or \
           ("unique" in query and len(s["unique_characters"]) > 5):
            results.append(s)

    return jsonify(results), 200


# ---------- 5️⃣ DELETE /strings/<string_value> ----------
@app.route("/strings/<string_value>", methods=["DELETE"])
def delete_string(string_value):
    if string_value not in strings_data:
        return jsonify({"error": "String not found"}), 404
    del strings_data[string_value]
    return "", 204


# ---------- 6️⃣ Root ----------
@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the String Analyzer API",
        "routes": [
            "POST /strings",
            "GET /strings",
            "GET /strings/<string_value>",
            "DELETE /strings/<string_value>",
            "GET /strings/filter-by-natural-language"
        ]
    }), 200


if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="0.0.0.0", port=port)
