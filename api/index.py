# Simple Flask app to satisfy Vercel's Python entrypoint requirement.
# This is a placeholder serverless function. It does NOT run your Java/Gradle app.
# Deploy the Java backend elsewhere (Render, Fly, Cloud Run) and point this frontend or API to it.

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Placeholder app — backend must be deployed separately."})
