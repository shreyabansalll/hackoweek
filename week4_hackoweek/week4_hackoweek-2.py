#!/usr/bin/env python
# coding: utf-8

# In[5]:


get_ipython().system('pip install seaborn')


# In[7]:


import sys
print(sys.executable)


# In[8]:


import sys
get_ipython().system('{sys.executable} -m pip install seaborn')


# In[1]:


import seaborn as sns


# In[1]:


import pandas as pd
import numpy as np

np.random.seed(42)

# Generate hourly timestamps for 6 months
date_range = pd.date_range(start="2024-01-01", end="2024-06-30 23:00:00", freq="H")

df = pd.DataFrame()
df['datetime'] = date_range

# Extract features
df['date'] = df['datetime'].dt.date
df['hour'] = df['datetime'].dt.hour
df['day_of_week'] = df['datetime'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5,6]).astype(int)

# Generate temperature (seasonal + randomness)
df['temperature'] = (
    20 
    + 10 * np.sin(2 * np.pi * df.index / 720) 
    + np.random.normal(0, 3, len(df))
)

# Weather category based on temperature
df['weather_condition'] = np.where(
    df['temperature'] < 15, "Cold",
    np.where(df['temperature'] > 30, "Hot", "Moderate")
)

# Define lunch hours (11 AM – 2 PM)
df['is_lunch_hour'] = df['hour'].between(11, 14).astype(int)

# Base customer count
base_customers = 30 + (df['is_weekend'] * 10)

# Lunch surge effect
lunch_effect = df['is_lunch_hour'] * 40

# Weather effect
weather_effect = np.where(df['temperature'] > 30, -10, 0)

# Final customer count
df['customer_count'] = (
    base_customers
    + lunch_effect
    + weather_effect
    + np.random.normal(0, 5, len(df))
).astype(int)

df['customer_count'] = df['customer_count'].clip(lower=5)

# Average spend per customer
df['avg_spend'] = np.random.normal(12, 2, len(df))

df['revenue'] = df['customer_count'] * df['avg_spend']

# Define surge label (top 25% of lunch hours)
lunch_df = df[df['is_lunch_hour'] == 1]
threshold = lunch_df['customer_count'].quantile(0.75)

df['is_surge'] = (
    (df['is_lunch_hour'] == 1) &
    (df['customer_count'] > threshold)
).astype(int)

df.head()


# In[2]:


df.to_csv("restaurant_lunch_surge_dataset.csv", index=False)


# In[3]:


from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

# Use only lunch hours
lunch_data = df[df['is_lunch_hour'] == 1]

features = ['temperature', 'is_weekend']
target = 'customer_count'

X = lunch_data[features]
y = lunch_data[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

preds = model.predict(X_test)

print("R2 Score:", r2_score(y_test, preds))


# In[4]:


get_ipython().system('pip install websockets nest_asyncio')


# In[6]:


import asyncio
import nest_asyncio
import threading
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

import sys
get_ipython().system('{sys.executable} -m pip install websockets nest_asyncio')


# In[7]:


df = pd.read_csv("restaurant_lunch_surge_dataset.csv")

lunch_data = df[df['is_lunch_hour'] == 1]

features = ['temperature', 'is_weekend']
target = 'customer_count'

X = lunch_data[features]
y = lunch_data[target]

model = LinearRegression()
model.fit(X, y)


# In[10]:


import websockets


# In[11]:


async def send_predictions(websocket):
    for _, row in lunch_data.iterrows():
        X_input = np.array([[row['temperature'], row['is_weekend']]])
        prediction = model.predict(X_input)[0]

        data = {
            "datetime": row['datetime'],
            "predicted_customers": float(prediction)
        }

        await websocket.send(json.dumps(data))
        await asyncio.sleep(0.5)

async def start_server():
    async with websockets.serve(send_predictions, "localhost", 8765):
        await asyncio.Future()

def run_server():
    asyncio.run(start_server())

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

print("WebSocket server running...")


# In[12]:


import matplotlib.animation as animation

predictions = []

async def receive_data():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            predictions.append(data['predicted_customers'])

asyncio.ensure_future(receive_data())

plt.figure(figsize=(10,5))

def update(frame):
    plt.cla()
    plt.plot(predictions[-50:])
    plt.title("Real-Time Lunch Surge Prediction")
    plt.xlabel("Time Step")
    plt.ylabel("Predicted Customers")

ani = animation.FuncAnimation(plt.gcf(), update, interval=500)
plt.show()


# In[ ]:




