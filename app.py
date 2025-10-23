from flask import Flask, request, jsonify
import hashlib
import difflib
import os

app = Flask(__name__)

# In-memory database
strings_data = {}

# ----------- Utility Functions -----------

def check_length(value):
    return len(value)

def is_palindrome(value):
    """Check palindrome (case-insensitive, ignoring spaces)."""
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
    """Perform all analysis on the string."""
    return {
        "string": value,
        "length": check_length(value),
        "is_palindrome": is_palindrome(value),
        "word_count": word_count(value),
        "unique_characters": unique_characters(value),
        "frequency": get_frequency(value),
        "sha256": sha256_hash(value),
    }

# ----------- 1️⃣ POST /string -----------

@app.route("/string", methods=["POST"])
def create_string():
    """Analyze and store a new string."""
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


# ----------- 2️⃣ GET /string/<string_value> -----------

@app.route("/string/<string_value>", methods=["GET"])
def get_string(string_value):
    """Retrieve analysis for a specific string."""
    result = strings_data.get(string_value)
    if not result:
        return jsonify({"error": "String not found"}), 404
    return jsonify(result), 200


# ----------- 3️⃣ GET /string -----------

@app.route("/string", methods=["GET"])
def get_all_strings():
    """Retrieve all or filtered strings."""
    if not request.args:
        return jsonify(list(strings_data.values())), 200

    filtered = list(strings_data.values())

    # Filter by is_palindrome
    if "is_palindrome" in request.args:
        val = request.args.get("is_palindrome").lower()
        if val not in ["true", "false"]:
            return jsonify({"error": "is_palindrome must be true or false"}), 422
        bool_val = val == "true"
        filtered = [s for s in filtered if s["is_palindrome"] == bool_val]

    # Filter by length_gt
    if "length_gt" in request.args:
        try:
            limit = int(request.args.get("length_gt"))
            filtered = [s for s in filtered if s["length"] > limit]
        except ValueError:
            return jsonify({"error": "Invalid length_gt value"}), 422

    # Filter by word_count
    if "word_count" in request.args:
        try:
            count = int(request.args.get("word_count"))
            filtered = [s for s in filtered if s["word_count"] == count]
        except ValueError:
            return jsonify({"error": "Invalid word_count value"}), 422

    # Natural language parsing (basic keyword detection)
    if "query" in request.args:
        keyword = request.args.get("query").lower()
        filtered = [
            s for s in filtered
            if keyword in s["string"].lower()
            or keyword in s["sha256"]
        ]

    return jsonify(filtered), 200


# ----------- 4️⃣ DELETE /string/<string_value> -----------

@app.route("/string/<string_value>", methods=["DELETE"])
def delete_string(string_value):
    """Delete a specific string."""
    if string_value not in strings_data:
        return jsonify({"error": "String not found"}), 404
    del strings_data[string_value]
    return "", 204


# ----------- 5️⃣ GET /string/matches/<string_value> -----------

@app.route("/string/matches/<string_value>", methods=["GET"])
def find_matches(string_value):
    """Return similar strings to a given input."""
    if not strings_data:
        return jsonify({"error": "No strings available"}), 404

    all_strings = list(strings_data.keys())
    matches = difflib.get_close_matches(string_value, all_strings, n=5, cutoff=0.4)

    return jsonify({"matches": matches}), 200


# ----------- Root Route (for sanity check) -----------

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the String Analysis API!",
        "available_endpoints": [
            "POST /string",
            "GET /string",
            "GET /string/<string_value>",
            "DELETE /string/<string_value>",
            "GET /string/matches/<string_value>"
        ]
    }), 200


# ----------- Run server with dynamic port -----------

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="0.0.0.0", port=port)
