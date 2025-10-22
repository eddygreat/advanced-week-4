"""Test script that starts server and runs prediction test"""
import threading
import time
from web import app
import requests
import json
from sklearn.datasets import load_breast_cancer

def run_server():
    app.run(port=5000, debug=False)

# Start server in thread
server = threading.Thread(target=run_server)
server.daemon = True
server.start()

# Wait for server to start
time.sleep(2)

# Get feature names from the dataset
data = load_breast_cancer(as_frame=True)
X = data.frame.drop(columns=['target']).iloc[0]  # use first row as example, drop target

# Create sample features
features = {col: float(val) for col, val in X.items()}

# Make prediction request
url = 'http://127.0.0.1:5000/predict'
print('Sending features:', json.dumps(features, indent=2))
try:
    response = requests.post(url, json=features)
    print('\nResponse:', response.status_code)
    if response.ok:
        print('Prediction:', response.json())
    else:
        print('Error:', response.text)
except Exception as e:
    print('Error:', str(e))