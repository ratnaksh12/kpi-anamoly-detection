import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Create folder if not exists
os.makedirs("data", exist_ok=True)

# Generate 100 dates
dates = [datetime.today() - timedelta(days=i) for i in range(99, -1, -1)]

# Create realistic KPI values
np.random.seed(42)

revenue = np.random.normal(loc=10000, scale=800, size=100).round(2)
revenue[50] += 3000  # spike
revenue[75] -= 2500  # drop

daily_active_users = np.random.normal(loc=3200, scale=150, size=100).astype(int)
bounce_rate = np.clip(np.random.normal(loc=45, scale=3, size=100), 30, 60).round(1)

# Assemble DataFrame
df = pd.DataFrame({
    "date": [d.strftime("%Y-%m-%d") for d in dates],
    "revenue": revenue,
    "daily_active_users": daily_active_users,
    "bounce_rate": bounce_rate
})

# Save to CSV
df.to_csv("data/kpis.csv", index=False)
print("✅ data/kpis.csv generated!")
