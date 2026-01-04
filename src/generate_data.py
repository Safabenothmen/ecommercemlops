import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import sys

# Ajouter le répertoire parent au path pour les imports futurs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
np.random.seed(42)
random.seed(42)

NUM_EVENTS = 50000   # nombre total d'événements
start_date = datetime(2025, 1, 1)

# IDs utilisateurs et produits
user_ids = [f"user_{i:05d}" for i in range(1, 5001)]   # 5000 utilisateurs
product_ids = [f"prod_{i:04d}" for i in range(1, 501)] # 500 produits
categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty']

# Générer les timestamps (toutes les 5 minutes)
timestamps = [start_date + timedelta(minutes=5*i) for i in range(NUM_EVENTS)]

data = []
for ts in timestamps:
    user_id = random.choice(user_ids)
    product_id = random.choice(product_ids)
    category = random.choice(categories)

    # Simulation comportement utilisateur
    clicks = np.random.choice([1,2,3,4,5,10,15,20],
                              p=[0.3,0.25,0.2,0.1,0.08,0.04,0.02,0.01])
    cart_adds = np.random.choice([0,1,2,3], p=[0.6,0.3,0.08,0.02]) if clicks >= 5 else np.random.choice([0,1], p=[0.8,0.2])
    avg_price = {
        'Electronics': np.random.uniform(100,500),
        'Clothing': np.random.uniform(20,150),
        'Home': np.random.uniform(30,300),
        'Books': np.random.uniform(10,50),
        'Sports': np.random.uniform(25,200),
        'Beauty': np.random.uniform(15,100)
    }[category]

    time_on_page = clicks * np.random.uniform(10,60)
    hour_of_day = ts.hour
    day_of_week = ts.weekday()
    is_weekend = 1 if day_of_week >= 5 else 0
    products_viewed = np.random.randint(1,15)
    has_purchased_before = np.random.choice([0,1], p=[0.85,0.15])

    # Probabilité d'achat
    purchase_prob = 0.0
    if cart_adds > 0: purchase_prob += 0.3
    if clicks >= 5: purchase_prob += 0.15
    if time_on_page > 300: purchase_prob += 0.1
    if is_weekend: purchase_prob += 0.1
    if has_purchased_before: purchase_prob += 0.15
    if avg_price < 50: purchase_prob += 0.1
    if avg_price > 300: purchase_prob -= 0.15
    if products_viewed > 10: purchase_prob -= 0.05
    purchase_prob = max(0, min(1, purchase_prob))

    purchased = 1 if np.random.random() < purchase_prob else 0

    data.append({
        'timestamp': ts,
        'user_id': user_id,
        'product_id': product_id,
        'category': category,
        'clicks': clicks,
        'cart_adds': cart_adds,
        'avg_price': round(avg_price,2),
        'time_on_page': round(time_on_page,2),
        'hour_of_day': hour_of_day,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'products_viewed': products_viewed,
        'has_purchased_before': has_purchased_before,
        'purchased': purchased
    })

# Créer DataFrame
df = pd.DataFrame(data)

# Déterminer le chemin du dossier data à la racine
# Si ce script est dans src/, on remonte d'un niveau
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == 'src':
    project_root = os.path.dirname(current_dir)
else:
    project_root = current_dir

data_dir = os.path.join(project_root, "data", "raw")
os.makedirs(data_dir, exist_ok=True)

# Sauvegarde
file_path = os.path.join(data_dir, "user_events.csv")
df.to_csv(file_path, index=False)

print(f"✅ Dataset généré : {file_path}")
print(f"Nombre total d'événements : {len(df)}")
print(f"Taux de conversion : {df['purchased'].mean()*100:.2f}%")
print("\nAperçu des données :")
print(df.head())
print(f"\nColonnes disponibles : {list(df.columns)}")