from kafka import KafkaProducer
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
import random

print("=" * 60)
print("🚀 KAFKA PRODUCER - SIMULATION ÉVÉNEMENTS E-COMMERCE")
print("=" * 60)

# Configuration Kafka
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'user-events'

# Créer le producer
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',  # Attendre confirmation de tous les brokers
        retries=3
    )
    print(f"✅ Connecté au broker Kafka : {KAFKA_BROKER}")
    print(f"✅ Topic : {TOPIC_NAME}")
except Exception as e:
    print(f"❌ Erreur de connexion à Kafka : {e}")
    exit(1)

# Charger le dataset pour avoir des données réalistes
try:
    df = pd.read_csv('data/raw/user_events.csv')
    print(f"✅ Dataset chargé : {len(df):,} événements disponibles")
except FileNotFoundError:
    print("⚠️ Dataset non trouvé. Génération de données aléatoires...")
    df = None

# Catégories et utilisateurs
categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty']
user_ids = [f"user_{i:05d}" for i in range(1, 1001)]
product_ids = [f"prod_{i:04d}" for i in range(1, 501)]

def generate_event():
    """Génère un événement utilisateur réaliste"""
    
    if df is not None and random.random() < 0.7:
        # 70% du temps : prendre un événement réel du dataset
        event = df.sample(1).iloc[0].to_dict()
        # Mettre à jour le timestamp
        event['timestamp'] = datetime.now().isoformat()
        return event
    else:
        # 30% du temps : générer un nouvel événement
        category = random.choice(categories)
        
        # Générer des valeurs cohérentes
        clicks = np.random.choice([1, 2, 3, 4, 5, 10], p=[0.3, 0.25, 0.2, 0.15, 0.07, 0.03])
        
        if clicks >= 5:
            cart_adds = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
        elif clicks >= 3:
            cart_adds = np.random.choice([0, 1], p=[0.6, 0.4])
        else:
            cart_adds = np.random.choice([0, 1], p=[0.85, 0.15])
        
        # Prix selon catégorie
        price_ranges = {
            'Electronics': (100, 500),
            'Clothing': (20, 150),
            'Home': (30, 300),
            'Books': (10, 50),
            'Sports': (25, 200),
            'Beauty': (15, 100)
        }
        min_price, max_price = price_ranges[category]
        avg_price = round(np.random.uniform(min_price, max_price), 2)
        
        now = datetime.now()
        
        return {
            'timestamp': now.isoformat(),
            'user_id': random.choice(user_ids),
            'product_id': random.choice(product_ids),
            'category': category,
            'clicks': int(clicks),
            'cart_adds': int(cart_adds),
            'avg_price': float(avg_price),
            'time_on_page': round(clicks * np.random.uniform(10, 60), 2),
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'is_weekend': 1 if now.weekday() >= 5 else 0,
            'products_viewed': int(np.random.randint(1, 15)),
            'has_purchased_before': int(np.random.choice([0, 1], p=[0.85, 0.15]))
        }

# Compteurs
events_sent = 0
errors = 0

print("\n" + "=" * 60)
print("📡 ENVOI D'ÉVÉNEMENTS EN TEMPS RÉEL")
print("   Fréquence : 1 événement toutes les 5 secondes")
print("   Appuyez sur Ctrl+C pour arrêter")
print("=" * 60 + "\n")

try:
    while True:
        # Générer un événement
        event = generate_event()
        
        try:
            # Envoyer à Kafka
            future = producer.send(TOPIC_NAME, value=event)
            result = future.get(timeout=10)  # Attendre confirmation
            
            events_sent += 1
            
            # Afficher l'événement envoyé
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Événement #{events_sent}")
            print(f"   👤 User: {event['user_id']}")
            print(f"   📦 Product: {event['product_id']} ({event['category']})")
            print(f"   💰 Prix: {event['avg_price']}€")
            print(f"   🖱️ Clics: {event['clicks']} | 🛒 Panier: {event['cart_adds']}")
            print(f"   📊 Partition: {result.partition} | Offset: {result.offset}")
            print()
            
        except Exception as e:
            errors += 1
            print(f"❌ Erreur d'envoi : {e}\n")
        
        # Attendre 5 secondes avant le prochain événement
        time.sleep(300)
        
        # Afficher un résumé toutes les 20 événements
        if events_sent % 20 == 0:
            print("=" * 60)
            print(f"📊 RÉSUMÉ : {events_sent} événements envoyés | {errors} erreurs")
            print("=" * 60 + "\n")

except KeyboardInterrupt:
    print("\n" + "=" * 60)
    print("⏹️ ARRÊT DU PRODUCER")
    print("=" * 60)
    print(f"Total événements envoyés : {events_sent}")
    print(f"Total erreurs : {errors}")
    print(f"Taux de succès : {(events_sent/(events_sent+errors)*100):.2f}%" if (events_sent+errors) > 0 else "0%")
    
    # Fermer proprement le producer
    producer.flush()
    producer.close()
    print("✅ Producer fermé proprement")
    
except Exception as e:
    print(f"\n❌ Erreur critique : {e}")
    producer.close()