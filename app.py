from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_openapi3 import OpenAPI, Info
from pydantic import BaseModel, Field, ValidationError
import numpy as np
import joblib

# Inicializando Flask e Banco de Dados
info = Info(title="Water Quality API", version="1.0.0")
app = OpenAPI(__name__, info=info)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_quality.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Carregar o modelo SVM treinado
model = joblib.load('best_water_quality_model.pkl')

# Definindo o schema de entrada com Pydantic para validação
class WaterQualityInput(BaseModel):
    ph: float = Field(..., gt=0)
    hardness: float
    solids: float
    chloramines: float
    sulfate: float
    conductivity: float
    organic_carbon: float
    trihalomethanes: float
    turbidity: float

# Definindo o schema de resposta com Pydantic
class WaterQualityOutput(BaseModel):
    potability: int

# Modelo para mensagem de erro
class ErrorResponse(BaseModel):
    error: str

# Modelo para a resposta de sucesso
class SuccessResponse(BaseModel):
    message: str

# Modelo para remover
class DeletePath(BaseModel):
    id: int

# Modelo para a resposta da lista de entradas de qualidade de água
class WaterQualityEntry(BaseModel):
    id: int
    ph: float
    hardness: float
    solids: float
    chloramines: float
    sulfate: float
    conductivity: float
    organic_carbon: float
    trihalomethanes: float
    turbidity: float
    potability: int

# Modelo para encapsular a lista de entradas
class WaterQualityListResponse(BaseModel):
    entries: list[WaterQualityEntry]

# Definindo a tabela no banco de dados SQLAlchemy
class WaterQuality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ph = db.Column(db.Float, nullable=False)
    hardness = db.Column(db.Float, nullable=False)
    solids = db.Column(db.Float, nullable=False)
    chloramines = db.Column(db.Float, nullable=False)
    sulfate = db.Column(db.Float, nullable=False)
    conductivity = db.Column(db.Float, nullable=False)
    organic_carbon = db.Column(db.Float, nullable=False)
    trihalomethanes = db.Column(db.Float, nullable=False)
    turbidity = db.Column(db.Float, nullable=False)
    potability = db.Column(db.Integer, nullable=False)  # 0 ou 1

# Criar as tabelas no banco de dados dentro do contexto da aplicação Flask
with app.app_context():
    db.create_all()

# Rota para prever potabilidade e salvar no banco de dados
@app.post("/predict", responses={"200": WaterQualityOutput, "400": ErrorResponse, "500": ErrorResponse})
def predict(body: WaterQualityInput):
    try:
        # Extrair os dados do input
        data = body.model_dump()

        # Fazer a predição com o modelo SVM
        features = np.array([[data['ph'], data['hardness'], data['solids'], data['chloramines'],
                              data['sulfate'], data['conductivity'], data['organic_carbon'],
                              data['trihalomethanes'], data['turbidity']]])
        potability = model.predict(features)[0]

        # Criar nova entrada no banco de dados
        new_entry = WaterQuality(
            ph=data['ph'], hardness=data['hardness'], solids=data['solids'],
            chloramines=data['chloramines'], sulfate=data['sulfate'],
            conductivity=data['conductivity'], organic_carbon=data['organic_carbon'],
            trihalomethanes=data['trihalomethanes'], turbidity=data['turbidity'],
            potability=int(potability)
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify(WaterQualityOutput(potability=int(potability)).model_dump()), 200

    except ValidationError as e:
        return jsonify(ErrorResponse(error="Validation error").model_dump()), 400

    except Exception as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 500

# Rota para obter todas as entradas de qualidade de água
@app.get("/water_quality", responses={"200": WaterQualityListResponse})
def get_all_entries():
    entries = WaterQuality.query.all()
    entries = WaterQuality.query.all()
    output = [
        WaterQualityEntry(
            id=entry.id,
            ph=entry.ph,
            hardness=entry.hardness,
            solids=entry.solids,
            chloramines=entry.chloramines,
            sulfate=entry.sulfate,
            conductivity=entry.conductivity,
            organic_carbon=entry.organic_carbon,
            trihalomethanes=entry.trihalomethanes,
            turbidity=entry.turbidity,
            potability=entry.potability
        ) for entry in entries
    ]
    return jsonify(WaterQualityListResponse(entries=output).model_dump()), 200

# Rota para deletar uma entrada pelo ID
@app.delete("/water_quality/<int:id>", responses={"200": SuccessResponse, "404": ErrorResponse})
def delete_entry(path: DeletePath):
    entry = WaterQuality.query.get(path.id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify(SuccessResponse(message="Entry deleted").model_dump()), 200
    else:
        return jsonify(ErrorResponse(error="Entry not found").model_dump()), 404

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
