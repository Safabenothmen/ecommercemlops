import streamlit as st
import joblib
import json
import numpy as np

# Charger le modèle
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # remonte à D:\Mlops
MODEL_PATH = os.path.join(BASE_DIR, "models", "purchase_predictor.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "models", "feature_names.json")

model = joblib.load(MODEL_PATH)
with open(FEATURES_PATH, "r") as f:
    feature_names = json.load(f)


st.title("🛒 Prédiction d'Achat E-commerce")

# Formulaire Streamlit
clicks = st.number_input("🖱️ Nombre de clics", min_value=0, value=5)
cart_adds = st.number_input("🛒 Ajouts au panier", min_value=0, value=2)
avg_price = st.number_input("💰 Prix (€)", min_value=0.0, value=129.99)
time_on_page = st.number_input("⏱️ Temps sur page (secondes)", min_value=0.0, value=320.5)
hour_of_day = st.slider("🕐 Heure de la journée", 0, 23, 14)
day_of_week = st.selectbox("📅 Jour de la semaine", ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"], index=2)
is_weekend = st.selectbox("🏖️ Weekend ?", ["Non","Oui"])
products_viewed = st.number_input("👁️ Produits vus", min_value=1, value=8)
has_purchased_before = st.selectbox("🔄 Déjà acheté avant ?", ["Non","Oui"])
category = st.selectbox("🏷️ Catégorie", ["Electronics","Clothing","Home","Books","Sports","Beauty"])

if st.button("🔮 PRÉDIRE L'ACHAT"):
    # Préparer les données
    data = {
        "clicks": clicks,
        "cart_adds": cart_adds,
        "avg_price": avg_price,
        "time_on_page": time_on_page,
        "hour_of_day": hour_of_day,
        "day_of_week": ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"].index(day_of_week),
        "is_weekend": 1 if is_weekend=="Oui" else 0,
        "products_viewed": products_viewed,
        "has_purchased_before": 1 if has_purchased_before=="Oui" else 0
    }

    # One-hot encoding catégorie
    for cat in ["Electronics","Clothing","Home","Books","Sports","Beauty"]:
        data[f"cat_{cat}"] = 1 if category == cat else 0

    X = np.array([[data[name] for name in feature_names]])

    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0][1]

    # Confiance et reco
    if probability >= 0.7:
        confidence = "ÉLEVÉE"
        reco = "Afficher une promotion immédiate !"
    elif probability >= 0.4:
        confidence = "MOYENNE"
        reco = "Envoyer un email de rappel avec remise."
    elif probability >= 0.2:
        confidence = "FAIBLE"
        reco = "Proposer des produits similaires."
    else:
        confidence = "TRÈS FAIBLE"
        reco = "Ne pas insister."

    label = "ACHAT" if prediction else "PAS D'ACHAT"
    st.success(f"🎉 Prédiction : {label}")
    st.metric("Probabilité d'achat", f"{probability*100:.1f}%")
    st.write(f"Confiance : **{confidence}**")
    st.info(f"💡 Action recommandée : {reco}")
