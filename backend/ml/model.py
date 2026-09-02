import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_models(data_path="../cleaned_dataset.csv", model_dir="."):
    if not os.path.exists(data_path):
        from preprocessing.preprocess import preprocess_data
        df = preprocess_data()
    else:
        df = pd.read_csv(data_path)
        
    # We need a target variable 'suitability_score'. 
    # Since it's an unsupervised dataset for personalization, we create a synthetic 
    # historical suitability score for training based on general rating and cost efficiency.
    # In real life, this would be historical user ratings.
    max_cost = df['total_cost'].max()
    df['suitability_score'] = (df['rating'] / 5.0) * 60 + ((max_cost - df['total_cost']) / max_cost) * 40
    
    # Features
    X = df[['type_encoded', 'continent_encoded', 'duration', 'total_cost', 'rating']]
    y = df['suitability_score']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest (Primary)
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    
    print("Random Forest MSE:", mean_squared_error(y_test, rf_preds))
    print("Random Forest R2:", r2_score(y_test, rf_preds))
    
    # Train Decision Tree (Secondary)
    dt_model = DecisionTreeRegressor(random_state=42)
    dt_model.fit(X_train, y_train)
    dt_preds = dt_model.predict(X_test)
    
    print("Decision Tree MSE:", mean_squared_error(y_test, dt_preds))
    print("Decision Tree R2:", r2_score(y_test, dt_preds))
    
    # Save Random Forest Model
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(rf_model, os.path.join(model_dir, "rf_model.pkl"))
    print("Models trained and saved successfully.")

if __name__ == "__main__":
    train_models()
