from flask import flask, render_template,request,redirect,url_for,session,jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'

def get_db():
    return mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='senac',
        database='sistema_vagas_gdf'
    )

@pp.route('/')