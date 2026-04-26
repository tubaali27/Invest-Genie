import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
# import joblib  # Uncomment if you want to save the model

# 1. Load dataset
df = pd.read_csv(r"D:\stock_genie\all_stocks_data\combined_psx_data.csv")

# 2. Clean data
df.dropna(subset=['Close', 'SMA_30', 'RSI', 'Price_Change_Pct', 'Signal'], inplace=True)
df.replace([float('inf'), float('-inf')], pd.NA, inplace=True)
df.dropna(subset=['Close', 'SMA_30', 'RSI', 'Price_Change_Pct'], inplace=True)

# 3. Filter for Buy/Sell signals
df = df[df['Signal'].isin(['Buy', 'Sell'])]
df['Signal_Encoded'] = df['Signal'].map({'Buy': 0, 'Sell': 1})

# 4. Balance the dataset (undersampling)
buy = df[df['Signal'] == 'Buy']
sell = df[df['Signal'] == 'Sell']
n_samples = min(len(buy), len(sell))
buy_bal = resample(buy, replace=False, n_samples=n_samples, random_state=42)
sell_bal = resample(sell, replace=False, n_samples=n_samples, random_state=42)
df_balanced = pd.concat([buy_bal, sell_bal])

print("Balanced class distribution:\n", df_balanced['Signal'].value_counts())

# 5. Prepare features and target
features = ['Close', 'SMA_30', 'RSI', 'Price_Change_Pct']
X = df_balanced[features]
y = df_balanced['Signal_Encoded']

# 6. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 7. Pipeline: scaling + logistic regression
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('logreg', LogisticRegression(max_iter=200))
])
pipeline.fit(X_train, y_train)

# 8. Evaluation
y_pred = pipeline.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Buy', 'Sell']))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# 9. Save the trained model (uncomment to use)
# joblib.dump(pipeline, "Models_Joblib_Files/logistic_regression_model_buy_sell.pkl")
# print("Model saved as 'logistic_regression_model_buy_sell.pkl'")