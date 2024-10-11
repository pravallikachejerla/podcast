# utils.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os
from models import db, Podcast, ListenerData, PredictedListeners

def load_data():
    # Check if CSV files exist and have the correct format
    required_files = ['top_podcasts.csv', 'podcast_listeners.csv', 'predicted_listeners.csv']
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file {file} not found.")
    
    # Verify column names
    podcasts_df = pd.read_csv('top_podcasts.csv')
    listeners_df = pd.read_csv('podcast_listeners.csv')
    predictions_df = pd.read_csv('predicted_listeners.csv')
    
    expected_columns = {
        'top_podcasts.csv': ['title', 'author', 'description', 'image_url', 'category', 'subscribers'],
        'podcast_listeners.csv': ['date', 'daily_listeners'],
        'predicted_listeners.csv': ['predicted_listeners']
    }
    
    for file, df in [('top_podcasts.csv', podcasts_df), 
                     ('podcast_listeners.csv', listeners_df), 
                     ('predicted_listeners.csv', predictions_df)]:
        missing_columns = set(expected_columns[file]) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in {file}: {missing_columns}")

    # Load podcast data
    for _, row in podcasts_df.iterrows():
        podcast = Podcast(
            title=row['title'],
            author=row['author'],
            description=row['description'],
            image_url=row['image_url'],
            category=row['category'],
            subscribers=row['subscribers']
        )
        db.session.add(podcast)
    
    # Load listener data
    for _, row in listeners_df.iterrows():
        listener_data = ListenerData(
            date=datetime.strptime(row['date'].split()[0], '%Y-%m-%d').date(),
            daily_listeners=row['daily_listeners']
        )
        db.session.add(listener_data)
    
    # Load predicted listeners
    start_date = datetime.now().date()
    for i, row in predictions_df.iterrows():
        predicted_data = PredictedListeners(
            date=start_date + timedelta(days=i),
            predicted_listeners=row['predicted_listeners']
        )
        db.session.add(predicted_data)
    
    db.session.commit()

def get_podcast_growth_rate(podcast_id):
    # Mock function to calculate growth rate
    return np.random.uniform(0, 0.1)

def get_podcast_engagement_rate(podcast_id):
    # Mock function to calculate engagement rate
    return np.random.uniform(0.1, 0.5)

def predict_future_listeners(days=30):
    listener_data = ListenerData.query.order_by(ListenerData.date).all()
    X = np.array(range(len(listener_data))).reshape(-1, 1)
    y = np.array([data.daily_listeners for data in listener_data])
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.array(range(len(listener_data), len(listener_data) + days)).reshape(-1, 1)
    future_y = model.predict(future_X)
    
    return future_y
