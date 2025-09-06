from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
PASSWORD_CORRETTA = os.getenv("MINIAPP_PASSWORD")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    password = data.get("password")
    if password == PASSWORD_CORRETTA:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 401

if __name__ == "__main__":
    app.run(port=5000, debug=True)
