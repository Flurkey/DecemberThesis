import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("real_gesture_data.csv")
X = df.drop(columns=["label"])
y = df["label"]

model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X, y)

joblib.dump(model, "gesture_classifier_full.pkl")

print("Model re-trained and saved.")
