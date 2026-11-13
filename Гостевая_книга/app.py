
from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

FILE_NAME = "notes.json"


def load_notes():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


notes = load_notes()


def save_notes():
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(notes, file, ensure_ascii=False, indent=4)


def find_note(note_id):
    for note in notes:
        if note["id"] == note_id:
            return note
    return None


def valid_text(value):
    return isinstance(value, str) and bool(value.strip())


def get_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


@app.route("/notes", methods=["POST"])
def create_note():
    data = get_body()

    if not data or not valid_text(data.get("author")) or not valid_text(data.get("text")):
        return jsonify({"error": "author and text are required"}), 400

    note = {
        "id": max((n["id"] for n in notes), default=0) + 1,
        "author": data["author"],
        "text": data["text"],
        "likes": 0
    }

    notes.append(note)
    save_notes()

    return jsonify(note), 201


@app.route("/notes", methods=["GET"])
def get_notes():
    author = request.args.get("author")
    limit = request.args.get("limit", "10")
    offset = request.args.get("offset", "0")
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    try:
        limit = int(limit)
        offset = int(offset)
    except ValueError:
        return jsonify({"error": "Invalid limit or offset"}), 400

    if not 1 <= limit <= 100 or offset < 0:
        return jsonify({"error": "Invalid pagination values"}), 400

    if sort not in ("id", "likes"):
        return jsonify({"error": "Invalid sort"}), 400

    if order not in ("asc", "desc"):
        return jsonify({"error": "Invalid order"}), 400

    result = notes[:]

    if author is not None:
        result = [n for n in result if n["author"] == author]

    result.sort(key=lambda n: n[sort], reverse=(order == "desc"))

    return jsonify(result[offset:offset + limit]), 200


@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    note = find_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note), 200


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    note = find_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    data = get_body()

    if not data or not valid_text(data.get("author")) or not valid_text(data.get("text")):
        return jsonify({"error": "author and text are required"}), 400

    note["author"] = data["author"]
    note["text"] = data["text"]

    save_notes()
    return jsonify(note), 200


@app.route("/notes/<int:note_id>", methods=["PATCH"])
def patch_note(note_id):
    note = find_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    data = get_body()

    if not data or not any(key in data for key in ("author", "text")):
        return jsonify({"error": "No fields to update"}), 400

    for key in ("author", "text"):
        if key in data:
            if not valid_text(data[key]):
                return jsonify({"error": f"Invalid {key}"}), 400

    for key in ("author", "text"):
        if key in data:
            note[key] = data[key]

    save_notes()
    return jsonify(note), 200


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    note = find_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    notes.remove(note)
    save_notes()

    return jsonify({"deleted": note_id}), 200


@app.route("/notes/<int:note_id>/like", methods=["POST"])
def like_note(note_id):
    note = find_note(note_id)

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    note["likes"] += 1
    save_notes()

    return jsonify(note), 200


@app.route("/authors", methods=["GET"])
def get_authors():
    statistics = {}

    for note in notes:
        author = note["author"]

        if author not in statistics:
            statistics[author] = {
                "author": author,
                "notes": 0,
                "likes": 0
            }

        statistics[author]["notes"] += 1
        statistics[author]["likes"] += note["likes"]

    result = sorted(statistics.values(), key=lambda x: x["author"])

    return jsonify(result), 200


@app.route("/notes", methods=["DELETE"])
def delete_author_notes():
    author = request.args.get("author")

    if not valid_text(author):
        return jsonify({"error": "author is required"}), 400

    before = len(notes)
    notes[:] = [n for n in notes if n["author"] != author]
    deleted = before - len(notes)

    save_notes()

    return jsonify({"deleted": deleted}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
