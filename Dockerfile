# Image de base Python
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="safa@ecommerce-mlops.com"
LABEL description="E-commerce Purchase Prediction API"

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements
COPY requirements.txt .

# Installer les dépendances Python (sans upgrade pip, avec timeout)
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt -i https://pypi.org/simple

# Copier le code source
COPY src/ ./src/
COPY models/ ./models/

# Créer les dossiers nécessaires
RUN mkdir -p data/raw data/processed reports

# Exposer le port de l'API
EXPOSE 8000

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/models/purchase_predictor.pkl

# Commande de démarrage
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
