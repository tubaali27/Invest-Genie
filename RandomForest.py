import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.utils import resample
import numpy as np

# === Step 1: Load Combined Data ===
data = pd.read_csv(r"D:/STOCK_GENIE/all_stocks_data/combined_psx_data.csv")  # Use your actual path
print("📥 Data loaded successfully. Shape:")

# === Step 2: Features & Target ===
features = ["Close", "SMA_30", "RSI", "Price_Change_Pct"]
target = "Signal"
print("📊 Features: and target loaded")
# === Step 3: Clean & Prepare ===
data = data.dropna(subset=features + [target])
data = data[data[target].isin(["Buy", "Sell"])]  # Keep only Buy and Sell
print("🔧 Data cleaned and prepared. Shape:")
# === BALANCE THE DATASET ===
buy = data[data['Signal'] == 'Buy']
sell = data[data['Signal'] == 'Sell']

n_samples = min(len(buy), len(sell))
buy_down = resample(buy, replace=False, n_samples=n_samples, random_state=42)
sell_down = resample(sell, replace=False, n_samples=n_samples, random_state=42)
data_balanced = pd.concat([buy_down, sell_down])
print("Balanced class distribution:\n", data_balanced['Signal'].value_counts())

# === ENCODE LABELS ===
data_balanced["Signal_Encoded"] = data_balanced[target].map({"Buy": 0, "Sell": 1})

# === FEATURES AND TARGET ===
X = data_balanced[features]
y = data_balanced["Signal_Encoded"]
X = X.replace([np.inf, -np.inf], np.nan)
X = X.dropna()
y = y[X.index]

# === TRAIN/TEST SPLIT ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# === Step 5: Train Model ===
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
print("🤖 Model trained successfully.")
# === Step 6: Evaluate ===
y_pred = clf.predict(X_test)
print("📈 Predictions made on test set.")

print("📊 Accuracy:", accuracy_score(y_test, y_pred))
print("\n📄 Classification Report:\n", classification_report(y_test, y_pred, target_names=["Buy", "Sell"]))
print("\n🔀 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap="Blues", xticklabels=["Buy", "Sell"], yticklabels=["Buy", "Sell"])

# === Step 8: Save Model ===
# joblib.dump(clf, "Models_Joblib_Files/rf_stock_signal_model3.joblib")
# print("✅ Model trained and saved as rf_stock_signal_model3.joblib")
