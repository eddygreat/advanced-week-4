"""Test the /predict endpoint with sample data"""
import requests
import json
from sklearn.datasets import load_breast_cancer

# Get feature names from the dataset
data = load_breast_cancer(as_frame=True)
X = data.frame.iloc[0]  # use first row as example

# Create sample features
features = {col: float(val) for col, val in X.items()}

# Make prediction request (use port 5000 - Flask default)
url = 'http://127.0.0.1:5000/predict'
print('Sending features:', json.dumps(features, indent=2))
response = requests.post(url, json=features)

print('\nResponse:', response.status_code)
if response.ok:
    print('Prediction:', response.json())
else:
    print('Error:', response.text)