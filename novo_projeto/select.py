from flask import Flask, jsonify

app = Flask(__name__)

# 5 escolas falsas para teste
escolas = [
    {"id": 1, "nome": "Escola Municipal Brasília", "ra_id": 1},
    {"id": 2, "nome": "Escola Parque Norte", "ra_id": 1},
    {"id": 3, "nome": "Centro Educacional Cruzeiro", "ra_id": 2},
    {"id": 4, "nome": "Escola Modelo do Lago", "ra_id": 2},
    {"id": 5, "nome": "Colégio Distrito Federal", "ra_id": 3},
]


@app.get("/escolas/<int:ra_id>")
def escolas_por_ra(ra_id):
    escolas_da_ra = [
        {
            "id": escola["id"],
            "nome": escola["nome"]
        }
        for escola in escolas
        if escola["ra_id"] == ra_id
    ]

    return jsonify(escolas_da_ra)


if __name__ == "__main__":
    app.run(debug=True)
