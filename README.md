# API de Previsão da Qualidade da Água

Este projeto é uma **API de Previsão da Qualidade da Água** desenvolvida com Python, Flask, SQLAlchemy, OpenAPI 3 (Swagger) e Pydantic para validação de esquemas. A API prevê a potabilidade da água com base em vários parâmetros de qualidade e fornece uma interface CRUD para gerenciar as entradas de qualidade da água em um banco de dados SQLite.

## Funcionalidades

- **Previsão da potabilidade da água** usando um modelo SVM pré-treinado.
- **Operações CRUD** para entradas de qualidade da água armazenadas em um banco de dados SQLite.
- **Documentação OpenAPI 3** (Swagger) para interação e testes da API.
- **Validação de entradas** utilizando modelos Pydantic.
- **Persistência** de dados de qualidade da água em SQLite.

## Endpoints

### 1. **POST /predict**
   Faz a previsão da potabilidade da água com base nos parâmetros fornecidos e armazena o resultado no banco de dados.

   - **Corpo da Requisição**:
     ```json
     {
        "ph": 7.0,
        "hardness": 120.0,
        "solids": 10000.0,
        "chloramines": 8.0,
        "sulfate": 300.0,
        "conductivity": 450.0,
        "organic_carbon": 15.0,
        "trihalomethanes": 60.0,
        "turbidity": 4.0
     }
     ```

   - **Resposta** (Sucesso: 200):
     ```json
     {
        "potability": 1
     }
     ```

### 2. **GET /water_quality**
   Recupera todas as entradas de qualidade da água armazenadas no banco de dados.

   - **Resposta** (Sucesso: 200):
     ```json
     {
       "entries": [
         {
           "id": 1,
           "ph": 7.0,
           "hardness": 120.0,
           "solids": 10000.0,
           "chloramines": 8.0,
           "sulfate": 300.0,
           "conductivity": 450.0,
           "organic_carbon": 15.0,
           "trihalomethanes": 60.0,
           "turbidity": 4.0,
           "potability": 1
         }
       ]
     }
     ```

### 3. **DELETE /water_quality/{id}**
   Deleta uma entrada específica de qualidade da água no banco de dados pelo ID.

   - **Parâmetro de Caminho**:
     - `id` (inteiro): O ID da entrada a ser excluída.

   - **Resposta** (Sucesso: 200):
     ```json
     {
        "message": "Entry deleted"
     }
     ```

### 4. **Documentação Swagger**
   A API é documentada usando OpenAPI 3. Você pode acessar a documentação interativa Swagger navegando para:

   - **URL do Swagger**: `http://localhost:5000/openapi`

## Instalação e Configuração

### Pré-requisitos
Certifique-se de ter os seguintes itens instalados em seu sistema:

- Python 3.8+
- Docker (opcional, se você deseja rodar o projeto com Docker)

### Guia Passo a Passo

1. **Clonar o repositório**:
   ```bash
   git clone https://github.com/ViniciusCTeixeira/puc_mvp_back_water_quality.git
   cd puc_mvp_back_water_quality
   ```

2. **Criar e ativar um ambiente virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

3. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar a aplicação**:
   ```bash
   flask run
   ```

5. **Acessar a API**:
   - URL Base da API: `http://localhost:5000`
   - Documentação Swagger: `http://localhost:5000/openapi`

### Executando com Docker

1. **Construir a imagem Docker**:
   ```bash
   docker build -t puc_mvp_back_water_quality .
   ```

2. **Executar o container Docker**:
   ```bash
   docker run -p 5000:5000 puc_mvp_back_water_quality
   ```

3. **Acessar a API** via `http://localhost:5000`.

## Modelo e Conjunto de Dados

O modelo utilizado para prever a potabilidade da água é um modelo SVM treinado no [Water Quality Dataset](https://github.com/ViniciusCTeixeira/puc_mvp_dataset_water_quality). O modelo foi pré-treinado e salvo como um arquivo `.pkl`, que é carregado pela API.
1. **Comando para teste**:
   ```bash
   pytest -p no:warnings
   ```
   
## Estrutura do Projeto

```bash
.
├── app.py                  # Arquivo principal da aplicação
├── Dockerfile              # Configuração do Docker
├── requirements.txt        # Dependências do Python
├── best_water_quality_model.pkl  # Modelo pré-treinado
├── README.md               # Documentação do projeto
└── water_quality.db        # Banco de dados SQLite (gerado automaticamente)
```

## Dependências

- **Flask**: Microframework web para Python.
- **Flask-SQLAlchemy**: ORM para interagir com o banco de dados SQLite.
- **Flask-OpenAPI3**: Gera documentação Swagger para a API.
- **Pydantic**: Validação de dados e parsing.
- **Numpy**: Biblioteca para computação científica, usada para processamento de dados.
- **Joblib**: Para carregar o modelo de machine learning pré-treinado.