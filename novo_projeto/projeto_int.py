<<<<<<< HEAD

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
app = Flask(__name__)
app.secret_key= "chave_simples"

@app.route('/')
def home():
    usuario_logado = session.get('usuario') 
    return render_template('login.html', nome=usuario_logado)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    if email == 'admin@gmail.com' and senha == '123456':
        session ["usuario"] = "brendon"
        return redirect(url_for('home'))
    return "email ou senha incorretos" , 400
@app.route('/api/escolas')
def get_escolas():
    escolas = [
        {"id": 1, "nome": "Escola Classe 01"},
        {"id": 2, "nome": "Centro de Ensino Médio 02"}
    ]
    return jsonify(escolas)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

<<<<<<< HEAD
if __name__ == '__main__':
    app.run(debug=True)
 
=======
=======
from flask import flask, render_template,request,redirect,url_for,session,jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'

>>>>>>> 87a8d708145db2aef39bb226b61fd2582644a02e
def get_db():
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='senac',
        database='sistema_vagas_gdf'
<<<<<<< HEAD
=======
from flask import Flask,request,jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


app.config['MYSQl_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'senha'
app.config['MYSQL_DB'] = 'sistema'

mysql = MySQL(app)

@app.route('/usuarios' , methods=['POST'])
def criar_usuario():
    nome = request.json['nome']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO usuarios(nome) VALUES(%s)" ,
        (nome,)
>>>>>>> 96232fe6a1b2cf9ac5d94d6a06babc8334238528
    )
    mysql.connection.commit()
    return jsonify({"mensagem": "Usuario criado"})

app.route('/usuarios' , methods=['GET'])
def listar_usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    dados = cur.fetchall()

    usuarios = [
        {"id": u[0], "nome": u[1]}
        for u in dados

    ]

    return jsonify(usuarios)

if __name__ == '__main__':
    app.run(debug=True)






<<<<<<< HEAD
@pp.route('/')d
>>>>>>> 4b9feb47b501aa73c1ccdd287f79e58b30117ddd
=======
>>>>>>> 96232fe6a1b2cf9ac5d94d6a06babc8334238528
=======
    )

@pp.route('/')
>>>>>>> 87a8d708145db2aef39bb226b61fd2582644a02e
