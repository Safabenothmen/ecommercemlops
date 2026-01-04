import pandas as pd
import joblib
import os
from deepchecks.tabular import Dataset
from deepchecks.tabular.suites import (
    data_integrity,
    train_test_validation,
    model_evaluation
)
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("🔍 VALIDATION AVEC DEEPCHECKS")
print("=" * 60)

# Créer le dossier reports s'il n'existe pas
os.makedirs('reports', exist_ok=True)

# Charger les données
print("\n📂 Chargement des données...")
train_df = pd.read_csv('data/processed/train.csv')
test_df = pd.read_csv('data/processed/test.csv')
print(f"✅ Train : {len(train_df):,} lignes")
print(f"✅ Test  : {len(test_df):,} lignes")

# Charger le modèle
print("\n🤖 Chargement du modèle...")
model = joblib.load('models/purchase_predictor.pkl')
print(f"✅ Modèle chargé : {type(model).__name__}")

# Préparer les datasets Deepchecks
print("\n🔧 Préparation des datasets Deepchecks...")
cat_features = [col for col in train_df.columns if col.startswith('cat_')]
ds_train = Dataset(train_df, label='purchased', cat_features=cat_features)
ds_test = Dataset(test_df, label='purchased', cat_features=cat_features)
print(f"✅ Datasets Deepchecks créés ({len(cat_features)} features catégorielles)")

# ==========================================
# 1. VÉRIFICATION DE L'INTÉGRITÉ DES DONNÉES
# ==========================================
print("\n" + "=" * 60)
print("1️⃣ VÉRIFICATION DE L'INTÉGRITÉ DES DONNÉES")
print("=" * 60)

try:
    print("🔄 Exécution des checks d'intégrité...")
    data_suite = data_integrity()
    result_integrity = data_suite.run(ds_train)
    
    # Sauvegarder HTML (sans as_widget pour éviter problèmes JS)
    html_path = 'reports/data_integrity.html'
    result_integrity.save_as_html(html_path, as_widget=False)
    print(f"✅ HTML sauvegardé : {html_path}")
    
    # Sauvegarder PDF
    pdf_path = 'reports/data_integrity.pdf'
    result_integrity.save_as_pdf(pdf_path)
    print(f"✅ PDF sauvegardé : {pdf_path}")
    
except Exception as e:
    print(f"⚠️ Erreur lors de la vérification d'intégrité : {e}")
    print(f"   Type d'erreur : {type(e).__name__}")

# ==========================================
# 2. VALIDATION TRAIN/TEST
# ==========================================
print("\n" + "=" * 60)
print("2️⃣ VALIDATION TRAIN/TEST (Détection de Data Drift)")
print("=" * 60)

try:
    print("🔄 Exécution des checks train/test...")
    train_test_suite = train_test_validation()
    result_train_test = train_test_suite.run(ds_train, ds_test)
    
    # Sauvegarder HTML
    html_path = 'reports/train_test_validation.html'
    result_train_test.save_as_html(html_path, as_widget=False)
    print(f"✅ HTML sauvegardé : {html_path}")
    
    # Sauvegarder PDF
    pdf_path = 'reports/train_test_validation.pdf'
    result_train_test.save_as_pdf(pdf_path)
    print(f"✅ PDF sauvegardé : {pdf_path}")
    
except Exception as e:
    print(f"⚠️ Erreur lors de la validation train/test : {e}")
    print(f"   Type d'erreur : {type(e).__name__}")

# ==========================================
# 3. ÉVALUATION DU MODÈLE
# ==========================================
print("\n" + "=" * 60)
print("3️⃣ ÉVALUATION COMPLÈTE DU MODÈLE")
print("=" * 60)

try:
    print("🔄 Exécution des checks d'évaluation...")
    model_suite = model_evaluation()
    result_model = model_suite.run(ds_train, ds_test, model)
    
    # Sauvegarder HTML
    html_path = 'reports/model_evaluation.html'
    result_model.save_as_html(html_path, as_widget=False)
    print(f"✅ HTML sauvegardé : {html_path}")
    
    # Sauvegarder PDF
    pdf_path = 'reports/model_evaluation.pdf'
    result_model.save_as_pdf(pdf_path)
    print(f"✅ PDF sauvegardé : {pdf_path}")
    
except Exception as e:
    print(f"⚠️ Erreur lors de l'évaluation du modèle : {e}")
    print(f"   Type d'erreur : {type(e).__name__}")

# ==========================================
# 4. STATISTIQUES DE BASE
# ==========================================
print("\n" + "=" * 60)
print("4️⃣ STATISTIQUES DE BASE")
print("=" * 60)

train_conversion = train_df['purchased'].mean()
test_conversion = test_df['purchased'].mean()
print(f"\n📊 Taux de conversion :")
print(f"   Train : {train_conversion:.2%}")
print(f"   Test  : {test_conversion:.2%}")
print(f"   Différence : {abs(train_conversion - test_conversion):.2%}")
if abs(train_conversion - test_conversion) < 0.02:
    print("   ✅ Distributions similaires")
else:
    print("   ⚠️ Distributions différentes (possible data drift)")

train_missing = train_df.isnull().sum().sum()
test_missing = test_df.isnull().sum().sum()
print(f"\n🔍 Valeurs manquantes :")
print(f"   Train : {train_missing}")
print(f"   Test  : {test_missing}")
if train_missing == 0 and test_missing == 0:
    print("   ✅ Pas de valeurs manquantes")
else:
    print(f"   ⚠️ Valeurs manquantes détectées")

# Statistiques supplémentaires
print(f"\n💰 Statistiques des prix :")
print(f"   Train - Moyenne : {train_df['avg_price'].mean():.2f}€")
print(f"   Test  - Moyenne : {test_df['avg_price'].mean():.2f}€")

print(f"\n🖱️ Statistiques des clics :")
print(f"   Train - Moyenne : {train_df['clicks'].mean():.2f}")
print(f"   Test  - Moyenne : {test_df['clicks'].mean():.2f}")

# ==========================================
# RÉSUMÉ FINAL
# ==========================================
print("\n" + "=" * 60)
print("📋 RÉSUMÉ DE LA VALIDATION")
print("=" * 60)

print(f"\n📂 Rapports générés dans le dossier 'reports/' :\n")

# Vérifier les fichiers créés
reports = [
    ('data_integrity.html', 'data_integrity.pdf'),
    ('train_test_validation.html', 'train_test_validation.pdf'),
    ('model_evaluation.html', 'model_evaluation.pdf')
]

for html_file, pdf_file in reports:
    html_exists = os.path.exists(f'reports/{html_file}')
    pdf_exists = os.path.exists(f'reports/{pdf_file}')
    
    html_status = "✅" if html_exists else "❌"
    pdf_status = "✅" if pdf_exists else "❌"
    
    print(f"   {html_status} {html_file}")
    print(f"   {pdf_status} {pdf_file}")
    print()

print("💡 Recommandations :")
print("   → Si les HTML sont blancs : Ouvrir les PDF")
print("   → Si les PDF ne s'ouvrent pas : pip install --upgrade deepchecks")
print("   → Les PDF sont plus fiables que les HTML")

print("\n" + "=" * 60)
print("✅ VALIDATION TERMINÉE")
print("=" * 60)