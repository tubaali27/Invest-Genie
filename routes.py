from flask import Blueprint, render_template, request
from technical_analysis.psx_data_reader import data_reader
import joblib
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from collections import Counter
import os

technical_bp = Blueprint('technical', __name__)


# Load all 3 models using absolute paths
base_path = os.path.dirname(__file__)
logreg_model = joblib.load(os.path.join(base_path, "Models_Joblib_Files", "logistic_regression_model_buy_sell.pkl"))
svm_model = joblib.load(os.path.join(base_path, "Models_Joblib_Files", "svm_model_buy_sell_final.pkl"))
rf_model = joblib.load(os.path.join(base_path, "Models_Joblib_Files", "rf_stock_signal_model3.joblib"))
# Only Buy and Sell
label_map = {0: "Buy", 1: "Sell"}

def ensemble_predict(features):
    X = np.array([features])  # Reshape for model input

    pred_log = logreg_model.predict(X)[0]
    pred_svm = svm_model.predict(X)[0]
    pred_rf = rf_model.predict(X)[0]

    votes = [pred_log, pred_svm, pred_rf]
    final = Counter(votes).most_common(1)[0][0]

    return {
        "Logistic": label_map.get(pred_log, "Unknown"),
        "SVM": label_map.get(pred_svm, "Unknown"),
        "RandomForest": label_map.get(pred_rf, "Unknown"),
        "Final": label_map.get(final, "Unknown")
    }

@technical_bp.route("/", methods=["GET", "POST"])
def technical_home():
    prediction = None
    features = None
    error = None
    chart_data = None
    stock_name = None
    result = None

    if request.method == "POST":
        stock = request.form["stock"].strip().upper()
        stock_name = stock
        end_date = date.today()
        start_date = end_date - relativedelta(months=6)
        data = data_reader.stocks(stock, start_date, end_date)

        if data.empty:
            error = "No data found for the given stock symbol."
        else:
            latest = data.iloc[-1]  
            features = {
                "Close": latest["Close"],
                "SMA_30": latest["SMA_30"],
                "RSI": latest["RSI"],
                "Price_Change_Pct": latest["Price_Change_Pct"],
            }
            # Ensure the order matches training!
            input_features = [
                features["Close"],
                features["SMA_30"],
                features["RSI"],
                features["Price_Change_Pct"]
            ]
            result = ensemble_predict(input_features)
            prediction = result["Final"]

            chart_data = {
                "TIME": data.index.strftime("%Y-%m-%d").tolist(),
                "CLOSE": data["Close"].tolist(),
            }

    return render_template(
        "technical.html",
        prediction=prediction,
        features=features,
        error=error,
        chart_data=chart_data,
        result=result,
        stock_name=stock_name
    )