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


# In[2]:


# Core
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt

# Modeling
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Time
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")


# In[4]:


#Loading dataset
df = pd.read_csv("/Users/shreya/Downloads/restaurant_sales_data.csv")

df.head()
df.info()


# In[8]:


# Convert date column
df['date'] = pd.to_datetime(df['date'])

# Sort
df = df.sort_values('date')

# Drop missing
df = df.dropna()

df.describe()


# In[9]:


df['revenue'] = df['quantity_sold'] * df['actual_selling_price']
df['profit'] = (df['actual_selling_price'] - df['typical_ingredient_cost']) * df['quantity_sold']


# In[10]:


df['day_of_week'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month
df['is_weekend'] = df['day_of_week'].isin([5,6]).astype(int)


# In[11]:


daily_revenue = df.groupby('date')['revenue'].sum()

plt.figure(figsize=(14,5))
plt.plot(daily_revenue)
plt.title("Total Daily Revenue")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.show()


# In[12]:


df.groupby('has_promotion')['quantity_sold'].mean()


# In[13]:


df.groupby('weather_condition')['quantity_sold'].mean()


# In[14]:


target = 'quantity_sold'

numeric_features = [
    'actual_selling_price',
    'typical_ingredient_cost',
    'day_of_week',
    'month',
    'is_weekend'
]

categorical_features = [
    'restaurant_type',
    'meal_type',
    'weather_condition',
    'has_promotion',
    'special_event'
]


# In[15]:


split_date = df['date'].quantile(0.8)

train = df[df['date'] <= split_date]
test = df[df['date'] > split_date]

X_train = train[numeric_features + categorical_features]
y_train = train[target]

X_test = test[numeric_features + categorical_features]
y_test = test[target]


# In[17]:


from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])


# In[19]:


model.fit(X_train, y_train)

predictions = model.predict(X_test)


# In[20]:


mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

print("MAE:", mae)
print("RMSE:", rmse)
print("R2 Score:", r2)


# In[21]:


plt.figure(figsize=(14,5))
plt.plot(test['date'], y_test.values, label="Actual")
plt.plot(test['date'], predictions, label="Predicted")
plt.legend()
plt.title("Actual vs Predicted Demand")
plt.xticks(rotation=45)
plt.show()


# In[23]:


sample = X_test.iloc[0].copy()

price_range = np.linspace(
    df['actual_selling_price'].min(),
    df['actual_selling_price'].max(),
    50
)

profits = []

for price in price_range:
    sample['actual_selling_price'] = price
    predicted_qty = model.predict(sample.to_frame().T)[0]
    profit = (price - df['typical_ingredient_cost'].mean()) * predicted_qty
    profits.append(profit)

plt.plot(price_range, profits)
plt.xlabel("Price")
plt.ylabel("Estimated Profit")
plt.title("Profit vs Price")
plt.show()


# In[ ]:




