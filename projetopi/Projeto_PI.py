from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Chave usada para criptografar os dados da sessão
app.secret_key = 'sua_chave_secreta_aqui' 

# -----------------------------------------------------------------------------
# FUNÇÃO AUXILIAR: Conexão com o Banco de Dados
# -----------------------------------------------------------------------------
def get_db():
    """Abre e retorna uma conexão com o banco de dados MySQL."""
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='senac',
        database='sistema_vagas_gdf'
    )

# -----------------------------------------------------------------------------
# ROTAS PÚBLICAS E AUTENTICAÇÃO
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Pegamos os dados do formulário
        name = request.form['name']
        email = request.form['email']
        # Criptografamos a senha antes de salvar no banco (Boa prática de segurança!)
        password = generate_password_hash(request.form['password']) 
        
        # 2. Salvamos no banco de dados usando o 'with' (fecha a conexão automaticamente)
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (name, email, password))
                    conn.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return f"Erro ao cadastrar: {e}"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Busca o usuário pelo e-mail
        with get_db() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
        
        # Verifica se o usuário existe e se a senha está correta
        if user and check_password_hash(user['password'], password):
            # Salva os dados na Sessão (login ativo)
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
            
        return "E-mail ou senha incorretos!"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear() # Limpa a sessão (desloga o usuário)
    return redirect(url_for('index'))

# -----------------------------------------------------------------------------
# ROTAS DO SISTEMA (REQUEREM LOGIN)
# -----------------------------------------------------------------------------

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Proteção de Rota: se não tiver 'user_id' na sessão, manda para o login
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Se o usuário enviou o formulário de solicitação de vaga
    if request.method == 'POST':
        with get_db() as conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO requests (
                        user_id, student_name, cep, state, administrative_region, 
                        neighborhood, current_school, current_shift, desired_school, 
                        desired_shift, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pendente')
                """
                dados = (
                    session['user_id'], 
                    request.form['student_name'], request.form['cep'],
                    request.form['state'], request.form['administrative_region'],
                    request.form['neighborhood'], request.form['current_school'], 
                    request.form['current_shift'], request.form['desired_school'], 
                    request.form['desired_shift']
                )
                cursor.execute(sql, dados)
                conn.commit()
        return redirect(url_for('tracking'))

    # Se for requisição GET: Carrega as Regiões Administrativas para exibir na página
    with get_db() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT DISTINCT administrative_region FROM schools ORDER BY administrative_region")
            regions = cursor.fetchall()

    return render_template('dashboard.html', regions=regions)


@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    with get_db() as conn:
        # Se for um POST, significa que o usuário enviou uma mensagem na caixa de chat
        if request.method == 'POST' and 'message' in request.form:
            with conn.cursor() as cursor:
                sql = "INSERT INTO messages (request_id, sender_name, message) VALUES (%s, %s, %s)"
                cursor.execute(sql, (request.form['request_id'], session['user_name'], request.form['message']))
                conn.commit()
            return redirect(url_for('tracking'))

        # Se for GET: Busca todas as solicitações do usuário e suas respectivas mensagens
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM requests WHERE user_id = %s", (session['user_id'],))
            user_requests = cursor.fetchall()

            # Mapeia as mensagens por ID da solicitação
            messages = {}
            for req in user_requests:
                cursor.execute("SELECT * FROM messages WHERE request_id = %s ORDER BY created_at ASC", (req['id'],))
                messages[req['id']] = cursor.fetchall()

    return render_template('tracking.html', requests=user_requests, messages=messages)


@app.route('/cancel_request/<int:request_id>')
def cancel_request(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Apaga apenas se a solicitação pertencer ao usuário logado (segurança!)
            cursor.execute("DELETE FROM requests WHERE id = %s AND user_id = %s", (request_id, session['user_id']))
            conn.commit()

    return redirect(url_for('tracking'))

# -----------------------------------------------------------------------------
# API AUXILIAR (Para carregar dados com JS no Front-End)
# -----------------------------------------------------------------------------

@app.route('/api/schools/<region>')
def get_schools_by_region(region):
    """Retorna uma lista JSON de escolas com base na região selecionada."""
    with get_db() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT school_name FROM schools WHERE administrative_region = %s", (region,))
            schools = cursor.fetchall()
            
    return jsonify(schools)


if __name__ == '__main__':
    app.run(debug=True)