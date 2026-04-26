import pandas as pd
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.utils import resample
import joblib

# === Step 1: Load your dataset ===
df = pd.read_csv(r"D:/STOCK_GENIE/all_stocks_data/combined_psx_data.csv")   # Update path if needed

# === Step 2: Clean and prepare the data ===
df.dropna(subset=['Close', 'SMA_30', 'RSI', 'Price_Change_Pct', 'Signal'], inplace=True)
df.replace([float('inf'), float('-inf')], pd.NA, inplace=True)
df.dropna(subset=['Close', 'SMA_30', 'RSI', 'Price_Change_Pct'], inplace=True)

# Only keep Buy and Sell
df = df[df['Signal'].isin(['Buy', 'Sell'])]

# Encode signals
label_map = {'Buy': 0, 'Sell': 1}
df['Signal_Encoded'] = df['Signal'].map(label_map)

# === Step 3: BALANCE THE DATASET ===

# --- UNDERSAMPLING ---
buy = df[df['Signal'] == 'Buy']
sell = df[df['Signal'] == 'Sell']
n_samples = min(len(buy), len(sell))
buy_bal = resample(buy, replace=False, n_samples=n_samples, random_state=42)
sell_bal = resample(sell, replace=False, n_samples=n_samples, random_state=42)
df_balanced = pd.concat([buy_bal, sell_bal])

# --- OVERSAMPLING (Uncomment to use instead of undersampling) ---
# buy = df[df['Signal'] == 'Buy']
# sell = df[df['Signal'] == 'Sell']
# n_samples = max(len(buy), len(sell))
# buy_bal = resample(buy, replace=True, n_samples=n_samples, random_state=42)
# sell_bal = resample(sell, replace=True, n_samples=n_samples, random_state=42)
# df_balanced = pd.concat([buy_bal, sell_bal])

print("Balanced class distribution:\n", df_balanced['Signal'].value_counts())

# === Step 4: Select features and target (same order as RF/LogReg) ===
features = ['Close', 'SMA_30', 'RSI', 'Price_Change_Pct']
X = df_balanced[features]
y = df_balanced['Signal_Encoded']

# === Step 5: Split into training and test sets ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# === Step 6: Build the pipeline ===
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(kernel='rbf', C=1.0, gamma='scale'))
])

# === Step 7: Train the SVM model ===
pipeline.fit(X_train, y_train)

# === Step 8: Evaluate performance ===
y_pred = pipeline.predict(X_test)
print("📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Buy', 'Sell']))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# === Step 9: Save the model ===
# joblib.dump(pipeline, "Models_Joblib_Files/svm_model_buy_sell_final.pkl")
# print("✅ SVM model saved as 'Models_Joblib_Files/svm_model_buy_sell_final.pkl'")