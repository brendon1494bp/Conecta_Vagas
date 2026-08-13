from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='senac',
        database='sistema_vagas_gdf'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            conn.commit()
        except Exception as e:
            return f"Erro: {e}"
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        return "E-mail ou senha incorretos!"
    return render_template('login.html')

# Rota para buscar as regiões administrativas cadastradas para popular o select
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar lista de RAs únicas para o formulário
    cursor.execute("SELECT DISTINCT administrative_region FROM schools ORDER BY administrative_region")
    regions = cursor.fetchall()

    if request.method == 'POST':
        cursor.close()
        cursor_insert = conn.cursor()
        cursor_insert.execute("""
            INSERT INTO requests (user_id, student_name, cep, state, administrative_region, neighborhood, current_school, current_shift, desired_school, desired_shift, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pendente')
        """, (
            session['user_id'], 
            request.form['student_name'], 
            request.form['cep'],
            request.form['state'],
            request.form['administrative_region'],
            request.form['neighborhood'],
            request.form['current_school'], 
            request.form['current_shift'], 
            request.form['desired_school'], 
            request.form['desired_shift']
        ))
        conn.commit()
        cursor_insert.close()
        conn.close()
        return redirect(url_for('tracking'))
        
    cursor.close()
    conn.close()
    return render_template('dashboard.html', regions=regions)


@app.route('/api/schools/<region>')
def get_schools_by_region(region):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT school_name FROM schools WHERE administrative_region = %s", (region,))
    schools = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(schools)

@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM requests WHERE user_id = %s", (session['user_id'],))
    user_requests = cursor.fetchall()
    
    if request.method == 'POST' and 'message' in request.form:
        cursor.execute("INSERT INTO messages (request_id, sender_name, message) VALUES (%s, %s, %s)",
                       (request.form['request_id'], session['user_name'], request.form['message']))
        conn.commit()
        return redirect(url_for('tracking'))

    messages = {}
    for req in user_requests:
        cursor.execute("SELECT * FROM messages WHERE request_id = %s ORDER BY created_at ASC", (req['id'],))
        messages[req['id']] = cursor.fetchall()
        
    cursor.close()
    conn.close()
    return render_template('tracking.html', requests=user_requests, messages=messages)

@app.route('/cancel_request/<int:request_id>')
def cancel_request(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM requests WHERE id = %s AND user_id = %s", (request_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('tracking'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)