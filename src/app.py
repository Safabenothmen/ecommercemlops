from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import joblib
import json
import numpy as np
import traceback

app = FastAPI(docs_url=None, redoc_url=None)

# Charger le modèle
try:
    model = joblib.load("models/purchase_predictor.pkl")
    with open("models/feature_names.json", "r") as f:
        feature_names = json.load(f)
    print("✅ Modèle chargé avec succès")
    print(f"✅ Nombre de features : {len(feature_names)}")
except Exception as e:
    print(f"❌ Erreur chargement modèle : {e}")
    model = None
    feature_names = None


def render_page(result=None, values=None, error=None):
    """Générer la page HTML"""

    # Valeurs par défaut
    v = values if values else {
        "clicks": 5, "cart_adds": 2, "avg_price": 129.99,
        "time_on_page": 320.5, "hour_of_day": 14, "day_of_week": 2,
        "is_weekend": 0, "products_viewed": 8, "has_purchased_before": 0,
        "category": "Electronics"
    }

    # Bloc résultat
    result_html = ""
    
    if error:
        result_html = f"""
        <div style="background:#dc3545;color:white;padding:30px;border-radius:15px;margin:30px 0;">
            <h2>❌ ERREUR</h2>
            <p style="font-size:1.2em;">{error}</p>
        </div>
        """
    elif result:
        prob = result["probability"] * 100
        is_buy = result["will_purchase"]
        bg = "#28a745" if is_buy else "#dc3545"
        title = "🎉 ACHAT PROBABLE" if is_buy else "❌ PAS D'ACHAT"
        
        result_html = f"""
        <div style="background:{bg};color:white;padding:30px;border-radius:15px;margin:30px 0;text-align:center;">
            <h2 style="margin:0 0 20px 0;font-size:2em;">{title}</h2>
            <p style="font-size:3.5em;font-weight:bold;margin:20px 0;">{prob:.1f}%</p>
            <p style="font-size:1.3em;margin:15px 0;">Confiance : <strong>{result['confidence']}</strong></p>
            <div style="background:rgba(0,0,0,0.2);padding:20px;border-radius:10px;margin-top:25px;text-align:left;">
                <strong style="font-size:1.2em;">💡 Action recommandée :</strong><br><br>
                <span style="font-size:1.1em;">{result['recommendation']}</span>
            </div>
        </div>
        """

    # HTML de la page
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prédiction d'Achat E-commerce</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .field {{
            display: flex;
            flex-direction: column;
        }}
        label {{
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 0.95em;
        }}
        input, select {{
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }}
        input:focus, select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        button {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 18px;
            border: none;
            border-radius: 10px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 Prédiction d'Achat</h1>
        
        <form method="POST" action="/">
            <div class="grid">
                <div class="field">
                    <label>🖱️ Nombre de clics</label>
                    <input type="number" name="clicks" value="{v['clicks']}" min="0" required>
                </div>
                
                <div class="field">
                    <label>🛒 Ajouts au panier</label>
                    <input type="number" name="cart_adds" value="{v['cart_adds']}" min="0" required>
                </div>
                
                <div class="field">
                    <label>💰 Prix (€)</label>
                    <input type="number" name="avg_price" value="{v['avg_price']}" step="0.01" min="0" required>
                </div>
                
                <div class="field">
                    <label>⏱️ Temps sur page (secondes)</label>
                    <input type="number" name="time_on_page" value="{v['time_on_page']}" step="0.1" min="0" required>
                </div>
                
                <div class="field">
                    <label>🕐 Heure de la journée (0-23)</label>
                    <input type="number" name="hour_of_day" value="{v['hour_of_day']}" min="0" max="23" required>
                </div>
                
                <div class="field">
                    <label>📅 Jour de la semaine</label>
                    <select name="day_of_week" required>
                        <option value="0" {'selected' if v['day_of_week']==0 else ''}>Lundi</option>
                        <option value="1" {'selected' if v['day_of_week']==1 else ''}>Mardi</option>
                        <option value="2" {'selected' if v['day_of_week']==2 else ''}>Mercredi</option>
                        <option value="3" {'selected' if v['day_of_week']==3 else ''}>Jeudi</option>
                        <option value="4" {'selected' if v['day_of_week']==4 else ''}>Vendredi</option>
                        <option value="5" {'selected' if v['day_of_week']==5 else ''}>Samedi</option>
                        <option value="6" {'selected' if v['day_of_week']==6 else ''}>Dimanche</option>
                    </select>
                </div>
                
                <div class="field">
                    <label>🏖️ Weekend ?</label>
                    <select name="is_weekend" required>
                        <option value="0" {'selected' if v['is_weekend']==0 else ''}>Non</option>
                        <option value="1" {'selected' if v['is_weekend']==1 else ''}>Oui</option>
                    </select>
                </div>
                
                <div class="field">
                    <label>👁️ Produits vus</label>
                    <input type="number" name="products_viewed" value="{v['products_viewed']}" min="1" required>
                </div>
                
                <div class="field">
                    <label>🔄 Déjà acheté avant ?</label>
                    <select name="has_purchased_before" required>
                        <option value="0" {'selected' if v['has_purchased_before']==0 else ''}>Non</option>
                        <option value="1" {'selected' if v['has_purchased_before']==1 else ''}>Oui</option>
                    </select>
                </div>
                
                <div class="field">
                    <label>🏷️ Catégorie</label>
                    <select name="category" required>
                        <option value="Electronics" {'selected' if v['category']=='Electronics' else ''}>Electronics</option>
                        <option value="Clothing" {'selected' if v['category']=='Clothing' else ''}>Clothing</option>
                        <option value="Home" {'selected' if v['category']=='Home' else ''}>Home</option>
                        <option value="Books" {'selected' if v['category']=='Books' else ''}>Books</option>
                        <option value="Sports" {'selected' if v['category']=='Sports' else ''}>Sports</option>
                        <option value="Beauty" {'selected' if v['category']=='Beauty' else ''}>Beauty</option>
                    </select>
                </div>
            </div>
            
            <button type="submit">🔮 PRÉDIRE L'ACHAT</button>
        </form>
        
        {result_html}
    </div>
</body>
</html>
    """
    
    return html


@app.get("/", response_class=HTMLResponse)
async def home():
    return render_page()
@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/", response_class=HTMLResponse)
async def predict(
    clicks: int = Form(...),
    cart_adds: int = Form(...),
    avg_price: float = Form(...),
    time_on_page: float = Form(...),
    hour_of_day: int = Form(...),
    day_of_week: int = Form(...),
    is_weekend: int = Form(...),
    products_viewed: int = Form(...),
    has_purchased_before: int = Form(...),
    category: str = Form(...)
):
    # Sauvegarder les valeurs du formulaire
    values = {
        "clicks": clicks,
        "cart_adds": cart_adds,
        "avg_price": avg_price,
        "time_on_page": time_on_page,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "products_viewed": products_viewed,
        "has_purchased_before": has_purchased_before,
        "category": category
    }
    
    # Vérifier que le modèle est chargé
    if model is None or feature_names is None:
        return render_page(values=values, error="Modèle non chargé. Vérifiez que les fichiers models/purchase_predictor.pkl et models/feature_names.json existent.")
    
    try:
        # Préparer les données
        data = {
            "clicks": clicks,
            "cart_adds": cart_adds,
            "avg_price": avg_price,
            "time_on_page": time_on_page,
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "products_viewed": products_viewed,
            "has_purchased_before": has_purchased_before
        }
        
        # One-hot encoding de la catégorie
        for cat in ["Electronics", "Clothing", "Home", "Books", "Sports", "Beauty"]:
            data[f"cat_{cat}"] = 1 if category == cat else 0
        
        # Créer le vecteur de features dans le bon ordre
        X = np.array([[data[name] for name in feature_names]])
        
        print(f"📊 Shape X : {X.shape}")
        print(f"📊 Features : {feature_names}")
        
        # Prédiction
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0][1]
        
        print(f"✅ Prédiction : {prediction}")
        print(f"✅ Probabilité : {probability:.2%}")
        
        # Déterminer le niveau de confiance
        if probability >= 0.7:
            confidence = "ÉLEVÉE"
            reco = "Afficher une promotion immédiate ! L'utilisateur est très intéressé."
        elif probability >= 0.4:
            confidence = "MOYENNE"
            reco = "Envoyer un email de rappel dans les 24h avec une remise de 10%."
        elif probability >= 0.2:
            confidence = "FAIBLE"
            reco = "Proposer des produits similaires à prix réduit."
        else:
            confidence = "TRÈS FAIBLE"
            reco = "Ne pas insister. L'utilisateur n'est pas prêt à acheter."
        
        result = {
            "will_purchase": bool(prediction),
            "probability": float(probability),
            "confidence": confidence,
            "recommendation": reco
        }
        
        return render_page(result=result, values=values)
        
    except Exception as e:
        # En cas d'erreur, afficher le détail
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"❌ ERREUR : {error_detail}")
        print(traceback.format_exc())
        
        return render_page(values=values, error=f"Erreur lors de la prédiction : {error_detail}")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 SERVEUR LANCÉ")
    print("=" * 60)
    print("🌐 URL : http://localhost:8000")
    print("📊 Statut modèle :", "✅ Chargé" if model else "❌ Non chargé")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)