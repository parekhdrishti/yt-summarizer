"""
Trains a text classifier that predicts a video's category from its transcript text.

Pipeline: TF-IDF vectorizer -> Logistic Regression classifier.
Run this once to produce ml/category_model.joblib, which the app loads at runtime.
"""
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score


def main():
    df = pd.read_csv("ml/training_data.csv")
    print(f"Loaded {len(df)} labeled examples across categories: {sorted(df['category'].unique())}")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["category"], test_size=0.2, random_state=42, stratify=df["category"]
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=3000, ngram_range=(1, 2), stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000)),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(f"\nTest accuracy: {accuracy_score(y_test, y_pred):.2%}\n")
    print(classification_report(y_test, y_pred))

    joblib.dump(pipeline, "ml/category_model.joblib")
    print("Saved trained model to ml/category_model.joblib")


if __name__ == "__main__":
    main()