from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

usuarios = []


@app.get("/")
def inicio():
    return render_template("index.html")


@app.get("/cadastro")
def tela_cadastro():
    return render_template("cadastro.html")


@app.post("/cadastro")
def cadastro():
    dados = request.form

    usuarios.append({
        "nome": dados["nome"],
        "email": dados["email"],
        "senha": dados["senha"]
    })

    return "Cadastro realizado com sucesso!"


@app.get("/login")
def tela_login():
    return render_template("login.html")


@app.post("/login")
def login():
    email = request.form["email"]
    senha = request.form["senha"]

    for usuario in usuarios:
        if usuario["email"] == email and usuario["senha"] == senha:
            return render_template("dashboard.html")

    return "E-mail ou senha incorretos!", 401


@app.get("/acompanhamento")
def acompanhamento():
    return render_template("acompanhamento.html")


app.run(debug=True)