import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder
import random

def preprocess_data(filepath="../Tourist_Destinations.csv", output_path="../cleaned_dataset.csv"):
    # Load dataset
    df = pd.read_csv(filepath)
    
    # Handle missing values
    df = df.dropna()
    
    # Generate Mock Data for 'activities' and 'duration' as requested to match PRD
    activity_pool = ["Trekking", "Sightseeing", "Beach Volley", "Surfing", "Museum", "Shopping", "Food Tour", "Skiing"]
    df['activities'] = [",".join(random.sample(activity_pool, k=random.randint(1, 3))) for _ in range(len(df))]
    df['duration'] = [random.randint(3, 14) for _ in range(len(df))]
    
    # The dataset has: Destination Name,Country,Continent,Type,Avg Cost (USD/day),Best Season,Avg Rating,Annual Visitors (M),UNESCO Site
    # Rename for easier use
    df = df.rename(columns={
        "Destination Name": "destination",
        "Avg Cost (USD/day)": "cost",
        "Avg Rating": "rating",
        "Type": "type"
    })
    
    # Calculate total trip cost based on daily cost * duration
    df['total_cost'] = df['cost'] * df['duration']
    
    # Encode categorical features
    le = LabelEncoder()
    df['type_encoded'] = le.fit_transform(df['type'])
    df['continent_encoded'] = le.fit_transform(df['Continent'])
    
    # Save cleaned dataset
    df.to_csv(output_path, index=False)
    print(f"Data preprocessed and saved to {output_path}")
    
    return df

if __name__ == "__main__":
    # Test script locally
    preprocess_data()
