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
def get_db():
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='senac',
        database='sistema_vagas_gdf'
    )

@pp.route('/')d
>>>>>>> 4b9feb47b501aa73c1ccdd287f79e58b30117ddd
