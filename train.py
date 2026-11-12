"""Train the PhishGuard model: python train.py [path/to/data.csv]"""
import sys
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from features import FEATURE_NAMES, extract_features

path = sys.argv[1] if len(sys.argv) > 1 else "data/urls.csv"
df = pd.read_csv(path)  # columns: url,label  (1 = phishing, 0 = safe)

X = pd.DataFrame([extract_features(u) for u in df["url"]])[FEATURE_NAMES]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))
joblib.dump(model, "model/phishguard.joblib")
print("Model saved to model/phishguard.joblib")
