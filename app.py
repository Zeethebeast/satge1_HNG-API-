from flask import Flask, request, jsonify
import hashlib
import difflib

app = Flask(__name__)

# In-memory storage (dictionary)
strings_data = {}

# Utility functions
def check_length(value):
    return len(value)

def is_palindrome(value):
    cleaned = value.replace(" ", "").lower()
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
    return hashlib.sha256(value.encode()).hexdigest()

def analyze_string(value):
    return {
        "string": value,
        "length": check_length(value),
        "is_palindrome": is_palindrome(value),
        "word_count": word_count(value),
        "unique_characters": unique_characters(value),
        "frequency": get_frequency(value),
        "sha256": sha256_hash(value)
    }

# 1️⃣ POST /string → analyze and store a new string
@app.route("/string", methods=["POST"])
def create_string():
    data = request.get_json()

    if not data or "value" not in data:
        return jsonify({"error": "Missing 'value' field"}), 400

    value = data.get("value")

    if not isinstance(value, str):
        return jsonify({"error": "Value must be a string"}), 422

    if value in strings_data:
        return jsonify({"error": "Already exists"}), 429

    result = analyze_string(value)
    strings_data[value] = result

    return jsonify(result), 201


# 2️⃣ GET /string/<string_value> → Retrieve analysis of one string
@app.route("/string/<string_value>", methods=["GET"])
def get_string(string_value):
    result = strings_data.get(string_value)
    if not result:
        return jsonify({"error": "String not found"}), 404
    return jsonify(result), 200


# 3️⃣ GET /string → Retrieve all strings or filter by query params
@app.route("/string", methods=["GET"])
def get_all_strings():
    # if no query params → return all
    if not request.args:
        return jsonify(list(strings_data.values())), 200

    filtered = list(strings_data.values())

    # handle query parameters
    if "is_palindrome" in request.args:
        val = request.args.get("is_palindrome").lower() == "true"
        filtered = [s for s in filtered if s["is_palindrome"] == val]

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


# 4️⃣ DELETE /string/<string_value> → Delete a specific string
@app.route("/string/<string_value>", methods=["DELETE"])
def delete_string(string_value):
    if string_value not in strings_data:
        return jsonify({"error": "String not found"}), 404
    del strings_data[string_value]
    return "", 204


# 5️⃣ GET /string/matches/<string_value> → Find similar strings
@app.route("/string/matches/<string_value>", methods=["GET"])
def find_matches(string_value):
    if not strings_data:
        return jsonify({"error": "No strings available"}), 404

    all_strings = list(strings_data.keys())
    matches = difflib.get_close_matches(string_value, all_strings, n=5, cutoff=0.4)

    if not matches:
        return jsonify({"matches": []}), 200

    return jsonify({"matches": matches}), 200


if __name__ == "__main__":
    app.run(debug=True)
