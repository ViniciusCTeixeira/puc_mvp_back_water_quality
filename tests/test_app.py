import sys
import os
import joblib
import pytest
import pandas as pd
from sklearn.metrics import precision_score, recall_score, accuracy_score
from sklearn.model_selection import train_test_split

# Configurar o caminho para encontrar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, WaterQuality

# Definir os thresholds para precisão, recall e acurácia
ACCURACY_THRESHOLD = 0.8
PRECISION_THRESHOLD = 0.6
RECALL_THRESHOLD = 0.5

# Setup para o PyTest
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_water_quality.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# Fixture para carregar o modelo SVM
@pytest.fixture
def model():
    return joblib.load('best_water_quality_model.pkl')

# Fixture para carregar dados de teste aleatórios a partir do CSV
@pytest.fixture
def data():
    # Carregar o dataset de qualidade da água do CSV
    df = pd.read_csv('water_potability_test.csv')

    # Remover registros que contenham valores NaN
    df = df.dropna()

    # Separar as features e o alvo (potabilidade)
    X = df.drop('Potability', axis=1)
    y = df['Potability']

    # Dividir em treino e teste (opcional, caso queira separar os dados para teste)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=5, random_state=42)

    return X_test, y_test

# Testando a acurácia do modelo SVM com dados aleatórios do CSV
def test_model_accuracy(model, data):
    X_test, y_test = data

    # Fazer predições
    predictions = model.predict(X_test)

    # Calcular a acurácia
    accuracy = accuracy_score(y_test, predictions)
    assert accuracy >= ACCURACY_THRESHOLD, f"Acurácia do modelo é menor que {ACCURACY_THRESHOLD}: {accuracy}"

# Testando precisão e recall do modelo SVM
def test_category_precision_and_recall(model, data):
    X_test, y_test = data

    # Fazer predições
    predicted_labels = model.predict(X_test)

    # Calcular precisão e recall
    precision = precision_score(y_test, predicted_labels, average='weighted')
    recall = recall_score(y_test, predicted_labels, average='weighted')

    assert (precision >= PRECISION_THRESHOLD).all(), f"Precisão menor que {PRECISION_THRESHOLD}: {precision}"
    assert (recall >= RECALL_THRESHOLD).all(), f"Recall menor que {RECALL_THRESHOLD}: {recall}"

# Testando predição válida
def test_valid_prediction(client):
    # Dados de entrada válidos
    data = {
        "ph": 7.0,
        "hardness": 150.0,
        "solids": 20000.0,
        "chloramines": 7.0,
        "sulfate": 300.0,
        "conductivity": 500.0,
        "organic_carbon": 15.0,
        "trihalomethanes": 80.0,
        "turbidity": 4.0
    }

    response = client.post("/predict", json=data)
    json_data = response.get_json()

    # Verificar se a resposta é sucesso (200 OK)
    assert response.status_code == 200
    assert "potability" in json_data  # Verificar se o campo 'potability' está presente

# Testando entrada inválida (pH fora do limite)
def test_invalid_ph_value(client):
    # Dados com valor de pH inválido
    data = {
        "ph": -5.0,  # Valor inválido
        "hardness": 150.0,
        "solids": 20000.0,
        "chloramines": 7.0,
        "sulfate": 300.0,
        "conductivity": 500.0,
        "organic_carbon": 15.0,
        "trihalomethanes": 80.0,
        "turbidity": 4.0
    }

    response = client.post("/predict", json=data)

    # Verificar se o retorno é um erro (422 Unprocessable Entity)
    assert response.status_code == 422

# Testando criação e obtenção de entradas no CRUD
def test_create_and_get_entries(client):
    # Dados de entrada válidos
    data = {
        "ph": 7.0,
        "hardness": 150.0,
        "solids": 20000.0,
        "chloramines": 7.0,
        "sulfate": 300.0,
        "conductivity": 500.0,
        "organic_carbon": 15.0,
        "trihalomethanes": 80.0,
        "turbidity": 4.0
    }

    # Fazer a predição e criar a entrada no banco
    client.post("/predict", json=data)

    # Verificar se a entrada foi criada com sucesso
    response = client.get("/water_quality")
    json_data = response.get_json()

    # Verificar se o status é 200 OK e há pelo menos uma entrada
    assert response.status_code == 200
    assert len(json_data) > 0

# Testando deleção de uma entrada no CRUD
def test_delete_entry(client):
    # Dados de entrada válidos
    data = {
        "ph": 7.0,
        "hardness": 150.0,
        "solids": 20000.0,
        "chloramines": 7.0,
        "sulfate": 300.0,
        "conductivity": 500.0,
        "organic_carbon": 15.0,
        "trihalomethanes": 80.0,
        "turbidity": 4.0
    }

    # Fazer a predição e criar a entrada no banco
    client.post("/predict", json=data)

    # Obter a entrada criada
    response = client.get("/water_quality")
    json_data = response.get_json()

    # Verificar se há pelo menos uma entrada
    if len(json_data['entries']) > 0:
        entry_id = json_data['entries'][0].get('id')
        assert entry_id is not None, "ID não encontrado na resposta"

        # Pegar o ID da primeira entrada e deletar
        delete_response = client.delete(f"/water_quality/{entry_id}")

        # Verificar se a entrada foi deletada com sucesso
        assert delete_response.status_code == 200
    else:
        assert False, "Nenhuma entrada encontrada na resposta"
