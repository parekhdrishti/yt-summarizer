import os
import joblib

_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "category_model.joblib")

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = joblib.load(_MODEL_PATH)
    return _model


def predict_category(transcript_text: str) -> dict:
    """Predict a video's category from its transcript text.

    Returns {"category": str, "confidence": float}.
    """
    model = _get_model()
    category = model.predict([transcript_text])[0]
    confidence = float(model.predict_proba([transcript_text]).max())
    return {"category": category, "confidence": round(confidence, 3)}