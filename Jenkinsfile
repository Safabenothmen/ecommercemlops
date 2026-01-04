pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'ecommerce-purchase-api'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        MLFLOW_TRACKING_URI = 'http://localhost:5000'
    }
    
    stages {
        
        // ==========================================
        // Stage 1 : Checkout du code
        // ==========================================
        stage('📥 Checkout Code') {
            steps {
                echo '🔄 Récupération du code depuis Git...'
                checkout scm
                echo '✅ Code récupéré avec succès'
            }
        }
        
        // ==========================================
        // Stage 2 : Installation des dépendances
        // ==========================================
        stage('📦 Install Dependencies') {
            steps {
                echo '📦 Installation des dépendances Python...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
                echo '✅ Dépendances installées'
            }
        }
        
        // ==========================================
        // Stage 3 : Génération du dataset
        // ==========================================
        stage('🔢 Generate Dataset') {
            steps {
                echo '🔢 Génération du dataset simulé...'
                sh '''
                    . venv/bin/activate
                    mkdir -p data/raw data/processed data/streaming
                    python src/generate_data.py
                '''
                echo '✅ Dataset généré'
            }
        }
        
        // ==========================================
        // Stage 4 : Entraînement du modèle
        // ==========================================
        stage('🤖 Train Model') {
            steps {
                echo '🤖 Entraînement du modèle ML...'
                sh '''
                    . venv/bin/activate
                    mkdir -p models reports
                    python src/train.py
                '''
                echo '✅ Modèle entraîné et sauvegardé'
            }
        }
        
        // ==========================================
        // Stage 5 : Validation avec Deepchecks
        // ==========================================
        stage('✅ Validate Model') {
            steps {
                echo '✅ Validation du modèle avec Deepchecks...'
                sh '''
                    . venv/bin/activate
                    python src/validate.py
                '''
                
                // Publier les rapports HTML
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'data_integrity.html,train_test_validation.html,model_evaluation.html',
                    reportName: 'Deepchecks Reports'
                ])
                
                echo '✅ Validation terminée'
            }
        }
        
        // ==========================================
        // Stage 6 : Tests unitaires de l'API
        // ==========================================
        stage('🧪 Test API') {
            steps {
                echo '🧪 Exécution des tests unitaires...'
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v --html=reports/pytest_report.html --self-contained-html || true
                '''
                
                // Publier le rapport de tests
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'pytest_report.html',
                    reportName: 'Pytest Report'
                ])
                
                echo '✅ Tests terminés'
            }
        }
        
        // ==========================================
        // Stage 7 : Build de l'image Docker
        // ==========================================
        stage('🐳 Build Docker Image') {
            steps {
                echo '🐳 Construction de l\'image Docker...'
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                '''
                echo '✅ Image Docker construite'
            }
        }
        
        // ==========================================
        // Stage 8 : Déploiement
        // ==========================================
        stage('🚀 Deploy') {
            steps {
                echo '🚀 Déploiement de l\'application...'
                sh '''
                    # Arrêter l'ancien conteneur s'il existe
                    docker stop ecommerce-api || true
                    docker rm ecommerce-api || true
                    
                    # Lancer le nouveau conteneur
                    docker run -d \
                        --name ecommerce-api \
                        -p 8000:8000 \
                        -v $(pwd)/models:/app/models \
                        -v $(pwd)/data:/app/data \
                        --restart unless-stopped \
                        ${DOCKER_IMAGE}:latest
                    
                    # Attendre que l'API soit prête
                    sleep 10
                    
                    # Vérifier que l'API répond
                    curl -f http://localhost:8000/health || exit 1
                '''
                echo '✅ Application déployée avec succès'
            }
        }
        
        // ==========================================
        // Stage 9 : Health Check
        // ==========================================
        stage('🏥 Health Check') {
            steps {
                echo '🏥 Vérification de santé de l\'API...'
                sh '''
                    # Tester l'endpoint /health
                    curl -f http://localhost:8000/health
                    
                    # Tester l'endpoint /
                    curl -f http://localhost:8000/
                    
                    # Tester une prédiction
                    curl -X POST http://localhost:8000/predict \
                        -H "Content-Type: application/json" \
                        -d '{
                            "clicks": 5,
                            "cart_adds": 2,
                            "avg_price": 129.99,
                            "time_on_page": 320.5,
                            "hour_of_day": 14,
                            "day_of_week": 2,
                            "is_weekend": 0,
                            "products_viewed": 8,
                            "has_purchased_before": 0,
                            "category": "Electronics"
                        }'
                '''
                echo '✅ API en bonne santé'
            }
        }
    }
    
    // ==========================================
    // Actions post-build
    // ==========================================
    post {
        success {
            echo '✅✅✅ PIPELINE RÉUSSI ! ✅✅✅'
            echo '🎉 Le modèle est en production'
            echo '🌐 API accessible sur : http://localhost:8000'
            echo '📊 Documentation : http://localhost:8000/docs'
            echo '📈 MLflow UI : http://localhost:5000'
            
            // Envoyer une notification (optionnel)
            // emailext (
            //     subject: "✅ Build #${env.BUILD_NUMBER} - SUCCESS",
            //     body: "Le pipeline MLOps a réussi ! API déployée.",
            //     to: "team@example.com"
            // )
        }
        
        failure {
            echo '❌❌❌ PIPELINE ÉCHOUÉ ! ❌❌❌'
            echo '🔍 Vérifier les logs pour identifier le problème'
            
            // Envoyer une notification d'échec
            // emailext (
            //     subject: "❌ Build #${env.BUILD_NUMBER} - FAILED",
            //     body: "Le pipeline MLOps a échoué. Vérifier Jenkins.",
            //     to: "team@example.com"
            // )
        }
        
        always {
            echo '🧹 Nettoyage...'
            
            // Archiver les artifacts
            archiveArtifacts artifacts: 'models/*.pkl, models/*.json, reports/*.html', allowEmptyArchive: true
            
            // Nettoyer les anciennes images Docker
            sh '''
                docker image prune -f --filter "until=168h"
            '''
            
            echo '✅ Pipeline terminé'
        }
    }
}