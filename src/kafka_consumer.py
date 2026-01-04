from kafka import KafkaConsumer
import json
import joblib
import numpy as np
from datetime import datetime
from elasticsearch import Elasticsearch
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("🎯 KAFKA CONSUMER - PRÉDICTIONS ML EN TEMPS RÉEL")
print("=" * 60)

# Configuration
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'user-events'
ELASTICSEARCH_HOST = 'http://localhost:9200'

# Charger le modèle ML
print("\n🤖 Chargement du modèle ML...")
try:
    model = joblib.load('models/purchase_predictor.pkl')
    with open('models/feature_names.json', 'r') as f:
        feature_names = json.load(f)
    print("✅ Modèle chargé avec succès")
except Exception as e:
    print(f"❌ Erreur de chargement du modèle : {e}")
    exit(1)

# Connexion à Elasticsearch (optionnel)
try:
    es = Elasticsearch([ELASTICSEARCH_HOST])
    if es.ping():
        print("✅ Connecté à Elasticsearch")
        
        # Créer l'index s'il n'existe pas
        index_name = 'ecommerce-predictions'
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name)
            print(f"✅ Index '{index_name}' créé")
    else:
        print("⚠️ Elasticsearch non disponible. Les prédictions ne seront pas sauvegardées.")
        es = None
except Exception as e:
    print(f"⚠️ Impossible de se connecter à Elasticsearch : {e}")
    es = None

# Créer le consumer Kafka
print(f"\n📡 Connexion au broker Kafka : {KAFKA_BROKER}")
try:
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',  # Lire uniquement les nouveaux messages
        enable_auto_commit=True,
        group_id='ml-prediction-group'
    )
    print(f"✅ Abonné au topic : {TOPIC_NAME}")
except Exception as e:
    print(f"❌ Erreur de connexion à Kafka : {e}")
    exit(1)

def prepare_features(event):
    """Préparer les features pour le modèle"""
    
    # Créer le dictionnaire de features
    features_dict = {
        'clicks': event['clicks'],
        'cart_adds': event['cart_adds'],
        'avg_price': event['avg_price'],
        'time_on_page': event['time_on_page'],
        'hour_of_day': event['hour_of_day'],
        'day_of_week': event['day_of_week'],
        'is_weekend': event['is_weekend'],
        'products_viewed': event['products_viewed'],
        'has_purchased_before': event['has_purchased_before']
    }
    
    # One-hot encoding pour la catégorie
    categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty']
    for cat in categories:
        features_dict[f'cat_{cat}'] = 1 if event['category'] == cat else 0
    
    # Créer le vecteur dans le bon ordre
    feature_vector = [features_dict[name] for name in feature_names]
    
    return np.array([feature_vector])

def save_to_elasticsearch(event, prediction, probability):
    """Sauvegarder la prédiction dans Elasticsearch"""
    
    if es is None:
        return
    
    try:
        document = {
            'timestamp': event['timestamp'],
            'user_id': event['user_id'],
            'product_id': event['product_id'],
            'category': event['category'],
            'price': event['avg_price'],
            'clicks': event['clicks'],
            'cart_adds': event['cart_adds'],
            'prediction': 'purchase' if prediction == 1 else 'no_purchase',
            'probability': float(probability),
            'processed_at': datetime.now().isoformat()
        }
        
        es.index(index='ecommerce-predictions', document=document)
    except Exception as e:
        print(f"⚠️ Erreur Elasticsearch : {e}")

# Compteurs et statistiques
total_processed = 0
predicted_purchases = 0
predicted_no_purchases = 0
high_prob_purchases = 0  # probabilité > 70%

print("\n" + "=" * 60)
print("👂 EN ÉCOUTE DES ÉVÉNEMENTS...")
print("   Appuyez sur Ctrl+C pour arrêter")
print("=" * 60 + "\n")

try:
    for message in consumer:
        event = message.value
        
        try:
            # Préparer les features
            features = prepare_features(event)
            
            # Faire la prédiction
            prediction = model.predict(features)[0]
            probability = model.predict_proba(features)[0][1]
            
            # Incrémenter les compteurs
            total_processed += 1
            
            if prediction == 1:
                predicted_purchases += 1
                if probability >= 0.7:
                    high_prob_purchases += 1
            else:
                predicted_no_purchases += 1
            
            # Afficher le résultat
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            if prediction == 1:
                emoji = "🛒" if probability >= 0.7 else "🔔"
                status = "ACHAT PROBABLE" if probability >= 0.7 else "Achat possible"
                color = "\033[92m"  # Vert
            else:
                emoji = "❌"
                status = "Pas d'achat"
                color = "\033[91m"  # Rouge
            
            reset = "\033[0m"  # Reset couleur
            
            print(f"{color}[{timestamp}] {emoji} {status}{reset}")
            print(f"   👤 User: {event['user_id']} | 📦 Product: {event['product_id']}")
            print(f"   🏷️ Catégorie: {event['category']} | 💰 Prix: {event['avg_price']}€")
            print(f"   🖱️ Clics: {event['clicks']} | 🛒 Panier: {event['cart_adds']}")
            print(f"   📊 Probabilité d'achat: {probability:.2%}")
            
            # Recommandation
            if probability >= 0.7:
                print(f"   💡 Action: MONTRER UNE PROMO MAINTENANT !")
            elif probability >= 0.4:
                print(f"   💡 Action: Envoyer email de rappel")
            elif probability >= 0.2:
                print(f"   💡 Action: Proposer produits similaires")
            else:
                print(f"   💡 Action: Ne pas spam")
            
            print()
            
            # Sauvegarder dans Elasticsearch
            save_to_elasticsearch(event, prediction, probability)
            
            # Afficher un résumé tous les 20 événements
            if total_processed % 20 == 0:
                conversion_rate = (predicted_purchases / total_processed) * 100
                high_prob_rate = (high_prob_purchases / total_processed) * 100
                
                print("=" * 60)
                print(f"📊 STATISTIQUES (après {total_processed} événements)")
                print("=" * 60)
                print(f"   🛒 Achats prédits: {predicted_purchases} ({conversion_rate:.1f}%)")
                print(f"   ❌ Pas d'achat: {predicted_no_purchases}")
                print(f"   🔥 Forte probabilité (>70%): {high_prob_purchases} ({high_prob_rate:.1f}%)")
                print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"❌ Erreur de traitement : {e}\n")
            continue

except KeyboardInterrupt:
    print("\n" + "=" * 60)
    print("⏹️ ARRÊT DU CONSUMER")
    print("=" * 60)
    
    if total_processed > 0:
        conversion_rate = (predicted_purchases / total_processed) * 100
        high_prob_rate = (high_prob_purchases / total_processed) * 100
        
        print(f"\n📊 RÉSUMÉ FINAL")
        print(f"   Total événements traités: {total_processed}")
        print(f"   Achats prédits: {predicted_purchases} ({conversion_rate:.1f}%)")
        print(f"   Pas d'achat: {predicted_no_purchases}")
        print(f"   Forte probabilité (>70%): {high_prob_purchases} ({high_prob_rate:.1f}%)")
    
    consumer.close()
    print("\n✅ Consumer fermé proprement")

except Exception as e:
    print(f"\n❌ Erreur critique : {e}")
    consumer.close()