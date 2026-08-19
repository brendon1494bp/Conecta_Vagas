from flask import Flask, request, jsonify
from flask_cors import CORS # 1. Adicione essa linha aqui em cima

app = Flask(__name__)
CORS(app) # 2. E adicione essa linha logo abaixo do app = Flask

escolas = [
    {"id": 1, "nome": "Escola Classe 01", "ra": "1"},
    {"id": 2, "nome": "Centro Educacional 01", "ra": "1"},
    {"id": 3, "nome": "Escola Classe 10", "ra": "2"},
    {"id": 4, "nome": "Centro Educacional 05", "ra": "3"}
]

@app.get("/escolas/buscar-por-ra")
def buscar_escolas():
    ra = request.args.get("ra")

    resultado = [escola for escola in escolas if escola["ra"] == ra]

    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True)