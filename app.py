"""PhishGuard Flask app: python app.py"""
import os
import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

from features import FEATURE_NAMES, explain, extract_features

app = Flask(__name__)
MODEL_PATH = "model/phishguard.joblib"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None


def analyze(url: str) -> dict:
    feats = extract_features(url)
    reasons = explain(feats)
    if model is not None:
        row = pd.DataFrame([feats])[FEATURE_NAMES]
        score = float(model.predict_proba(row)[0][1])
    else:  # fallback heuristic if no model is trained yet
        score = min(len(reasons) / 5, 1.0)
    verdict = "Phishing" if score >= 0.5 else "Likely safe"
    return {"url": url, "score": round(score * 100, 1),
            "verdict": verdict, "reasons": reasons}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def check():
    url = (request.get_json(silent=True) or {}).get("url", "").strip()
    if not url:
        return jsonify({"error": "Please provide a URL"}), 400
    return jsonify(analyze(url))


if __name__ == "__main__":
    # HOST=0.0.0.0 lets phones/laptops on the same Wi-Fi connect.
    # PORT is set automatically by hosting platforms.
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
