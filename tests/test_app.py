import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db, WaterQuality

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