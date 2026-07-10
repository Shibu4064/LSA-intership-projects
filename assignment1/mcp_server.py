"""
Minimal MCP server that wraps a trained TF-IDF + Logistic Regression
emotion classifier and exposes it as a Claude-callable tool.

Required files in the same folder:
  - emotion_model.joblib
  - label_names.txt

Install locally:
    pip install mcp joblib scikit-learn numpy

Test locally:
    mcp dev mcp_server.py
"""

import os
import numpy as np
import joblib
from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "emotion_model.joblib")
LABELS_PATH = os.path.join(HERE, "label_names.txt")

mcp = FastMCP("emotion-model")

_pipe = None
_label_names = None


def _load():
    global _pipe, _label_names
    if _pipe is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Missing model file: {MODEL_PATH}")
        if not os.path.exists(LABELS_PATH):
            raise FileNotFoundError(f"Missing labels file: {LABELS_PATH}")

        _pipe = joblib.load(MODEL_PATH)
        with open(LABELS_PATH, encoding="utf-8") as f:
            _label_names = [line.strip() for line in f if line.strip()]
    return _pipe, _label_names


@mcp.tool()
def predict_emotion(text: str, top_k_words: int = 6) -> dict:
    """Predict emotion for a short English text.

    Returns the predicted label, confidence, all class probabilities,
    and top weighted words/n-grams for the predicted class.
    """
    pipe, label_names = _load()

    probs = pipe.predict_proba([text])[0]
    pred_idx = int(np.argmax(probs))
    pred_label = label_names[pred_idx]

    vec = pipe.named_steps["tfidf"]
    clf = pipe.named_steps["clf"]
    feature_names = np.array(vec.get_feature_names_out())
    row = vec.transform([text])
    nonzero = row.nonzero()[1]

    top_words = []
    if len(nonzero) > 0:
        weights = clf.coef_[pred_idx][nonzero] * row[0, nonzero].toarray().ravel()
        order = np.argsort(-np.abs(weights))[:top_k_words]
        top_words = [
            {
                "term": str(feature_names[nonzero[i]]),
                "weight": round(float(weights[i]), 4),
                "direction": "supports" if weights[i] >= 0 else "opposes",
            }
            for i in order
        ]

    return {
        "text": text,
        "predicted_label": pred_label,
        "confidence": round(float(probs[pred_idx]), 4),
        "all_probabilities": {
            label_names[i]: round(float(p), 4) for i, p in enumerate(probs)
        },
        "top_contributing_words": top_words,
        "note": (
            "This is a simple linear TF-IDF classifier. It cannot reliably "
            "understand sarcasm, negation scope, or context beyond individual "
            "words and n-grams."
        ),
    }


@mcp.tool()
def dataset_label_distribution() -> dict:
    """Return the label names used by the trained emotion model."""
    _, label_names = _load()
    return {"labels": label_names}


if __name__ == "__main__":
    mcp.run(transport="stdio")
