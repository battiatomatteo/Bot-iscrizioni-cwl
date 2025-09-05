from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/api/iscritti")
def get_iscritti():
    try:
        with open("data/iscritti.json", "r", encoding="utf-8") as f:
            dati = json.load(f)
        return jsonify(dati.get("lista_principale", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
