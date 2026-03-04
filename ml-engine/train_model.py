import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load dataset (export from your DB)
data = pd.read_csv("transactions.csv")

# Features (you must match with Java)
X = data[["amount", "hour", "locationRisk", "velocityScore"]]
y = data["isFraud"]

# Scale data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_scaled, y)

# Save model + scaler
joblib.dump(model, "fraud_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model trained successfully")