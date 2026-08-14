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






