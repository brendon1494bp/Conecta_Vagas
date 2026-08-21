import os
import secrets
import smtplib
import sqlite3
from datetime import datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-me")
app.config["DATABASE"] = BASE_DIR / "conecta_vagas.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS ra (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS serie (id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS escola (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, id_ra INTEGER, endereco TEXT, telefone TEXT, email TEXT, FOREIGN KEY(id_ra) REFERENCES ra(id));
CREATE TABLE IF NOT EXISTS usuario (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE, senha TEXT NOT NULL, cpf TEXT UNIQUE, telefone TEXT, endereco TEXT);
CREATE TABLE IF NOT EXISTS solicitacao (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, endereco TEXT, id_serie INTEGER NOT NULL, id_escola_atual INTEGER NOT NULL, id_ra_desejada INTEGER, id_escola_desejada INTEGER, turno_atual TEXT NOT NULL, turno_desejado TEXT NOT NULL, id_usuario_responsavel INTEGER NOT NULL, motivo_troca TEXT, status TEXT NOT NULL DEFAULT 'AGUARDANDO_MATCH', data_criacao TEXT NOT NULL, data_atualizacao TEXT NOT NULL, FOREIGN KEY(id_usuario_responsavel) REFERENCES usuario(id));
CREATE TABLE IF NOT EXISTS match_troca (id INTEGER PRIMARY KEY AUTOINCREMENT, id_solicitacao_a INTEGER NOT NULL, id_solicitacao_b INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'ATIVO', data_hora_criacao TEXT NOT NULL, FOREIGN KEY(id_solicitacao_a) REFERENCES solicitacao(id), FOREIGN KEY(id_solicitacao_b) REFERENCES solicitacao(id));
CREATE TABLE IF NOT EXISTS mensagem (id INTEGER PRIMARY KEY AUTOINCREMENT, id_match INTEGER NOT NULL, mensagem TEXT NOT NULL, id_remetente INTEGER NOT NULL, lida INTEGER NOT NULL DEFAULT 0, tipo TEXT NOT NULL DEFAULT 'USUARIO', data_hora_envio TEXT NOT NULL, FOREIGN KEY(id_match) REFERENCES match_troca(id), FOREIGN KEY(id_remetente) REFERENCES usuario(id));
CREATE TABLE IF NOT EXISTS recuperacao (token TEXT PRIMARY KEY, id_usuario INTEGER NOT NULL, expira_em TEXT NOT NULL, usado INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS idx_escola_ra ON escola(id_ra);
CREATE INDEX IF NOT EXISTS idx_solicitacao_status ON solicitacao(status);
CREATE INDEX IF NOT EXISTS idx_solicitacao_usuario ON solicitacao(id_usuario_responsavel);
"""
RAs = [(1, "Plano Piloto"), (2, "Gama"), (3, "Taguatinga"), (4, "Brazlândia"), (5, "Sobradinho"), (6, "Planaltina"), (7, "Paranoá"), (8, "Núcleo Bandeirante"), (9, "Ceilândia"), (10, "Guará"), (11, "Cruzeiro"), (12, "Samambaia"), (13, "Santa Maria"), (14, "São Sebastião"), (15, "Recanto das Emas"), (16, "Lago Sul"), (17, "Riacho Fundo"), (18, "Lago Norte"), (19, "Candangolândia"), (20, "Águas Claras"), (21, "Riacho Fundo II"), (22, "Sudoeste/Octogonal"), (23, "Varjão"), (24, "Park Way"), (25, "SCIA/Estrutural"), (26, "Sobradinho II"), (27, "Jardim Botânico"), (28, "Itapoã"), (29, "SIA"), (30, "Vicente Pires"), (31, "Fercal"), (32, "Sol Nascente/Pôr do Sol"), (33, "Arniqueira"), (34, "Arapoanga"), (35, "Água Quente")]
SERIES = [(1, "Creche"), (2, "Pré-Escola - 1º Período"), (3, "Pré-Escola - 2º Período"), (4, "1º Ano - Ensino Fundamental I"), (5, "2º Ano - Ensino Fundamental I"), (6, "3º Ano - Ensino Fundamental I"), (7, "4º Ano - Ensino Fundamental I"), (8, "5º Ano - Ensino Fundamental I"), (9, "6º Ano - Ensino Fundamental II"), (10, "7º Ano - Ensino Fundamental II"), (11, "8º Ano - Ensino Fundamental II"), (12, "9º Ano - Ensino Fundamental II"), (13, "1ª Série - Ensino Médio"), (14, "2ª Série - Ensino Médio"), (15, "3ª Série - Ensino Médio")]
TURNOS = ("MATUTINO", "VESPERTINO", "NOTURNO", "INTEGRAL")
STATUS_DISPONIVEL = "AGUARDANDO_MATCH"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        if not g.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='usuario'").fetchone():
            preparar_banco(g.db)
    return g.db

@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db:
        db.close()

def preparar_banco(db):
    db.executescript(SCHEMA)
    colunas = {row[1] for row in db.execute("PRAGMA table_info(mensagem)")}
    if "tipo" not in colunas: db.execute("ALTER TABLE mensagem ADD COLUMN tipo TEXT NOT NULL DEFAULT 'USUARIO'")
    if "lida" not in colunas: db.execute("ALTER TABLE mensagem ADD COLUMN lida INTEGER NOT NULL DEFAULT 0")
    solicitacao_colunas = {row[1] for row in db.execute("PRAGMA table_info(solicitacao)")}
    if "status" not in solicitacao_colunas: db.execute("ALTER TABLE solicitacao ADD COLUMN status TEXT NOT NULL DEFAULT 'AGUARDANDO_MATCH'")
    if "data_criacao" not in solicitacao_colunas: db.execute("ALTER TABLE solicitacao ADD COLUMN data_criacao TEXT")
    if "data_atualizacao" not in solicitacao_colunas: db.execute("ALTER TABLE solicitacao ADD COLUMN data_atualizacao TEXT")
    escola_colunas = {row[1] for row in db.execute("PRAGMA table_info(escola)")}
    if "telefone" not in escola_colunas: db.execute("ALTER TABLE escola ADD COLUMN telefone TEXT")
    if "email" not in escola_colunas: db.execute("ALTER TABLE escola ADD COLUMN email TEXT")
    db.executemany("INSERT OR IGNORE INTO ra (id, nome) VALUES (?, ?)", RAs)
    db.executemany("INSERT OR IGNORE INTO serie (id, nome) VALUES (?, ?)", SERIES)
    escolas_sql = BASE_DIR / "dados" / "script_insert_escolas.sql"
    if escolas_sql.exists():
        try: db.executescript(escolas_sql.read_text(encoding="utf-8").replace("INSERT INTO escola", "INSERT OR IGNORE INTO escola"))
        except sqlite3.Error: pass
    db.execute("UPDATE solicitacao SET status='AGUARDANDO_MATCH' WHERE status='DISPONIVEL'")
    db.execute("UPDATE solicitacao SET turno_atual=UPPER(turno_atual), turno_desejado=UPPER(turno_desejado)")
    db.commit()

def init_db():
    db = sqlite3.connect(app.config["DATABASE"])
    preparar_banco(db)
    db.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Entre para continuar.", "warning"); return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def csrf_valid():
    return secrets.compare_digest(session.get("csrf", ""), request.form.get("csrf", ""))

def somente_digitos(valor, limite):
    return "".join(char for char in valor if char.isdigit())[:limite]

def cpf_valido(valor):
    cpf = somente_digitos(valor, 11)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[indice]) * (tamanho + 1 - indice) for indice in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[tamanho]):
            return False
    return True

@app.context_processor
def template_context():
    if "csrf" not in session: session["csrf"] = secrets.token_urlsafe(24)
    user = get_db().execute("SELECT * FROM usuario WHERE id = ?", (session["user_id"],)).fetchone() if session.get("user_id") else None
    unread = 0
    if user:
        unread = get_db().execute("SELECT COUNT(*) FROM mensagem m JOIN match_troca mt ON mt.id=m.id_match JOIN solicitacao a ON a.id=mt.id_solicitacao_a JOIN solicitacao b ON b.id=mt.id_solicitacao_b WHERE (a.id_usuario_responsavel=? OR b.id_usuario_responsavel=?) AND m.id_remetente != ? AND m.lida=0", (user["id"], user["id"], user["id"])).fetchone()[0]
    return {"current_user": user, "csrf": session["csrf"], "chat_nao_lidas": unread, "status_label": lambda status: {"AGUARDANDO_MATCH": "Aguardando match", "EM_NEGOCIACAO": "Em conversa", "CONCLUIDA": "Concluída", "CANCELADA": "Cancelada"}.get(status, status)}

@app.before_request
def protect_forms():
    if request.method == "POST" and not csrf_valid(): return "Requisição inválida (CSRF).", 400

@app.route("/")
def index(): return redirect(url_for("dashboard" if session.get("user_id") else "login"))

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email, senha = request.form.get("email", "").strip().lower(), request.form.get("senha", "")
        if not email or "@" not in email or len(senha) < 8 or senha != request.form.get("confirmacao"): flash("Informe e-mail válido e senhas iguais com pelo menos 8 caracteres.", "danger")
        elif get_db().execute("SELECT 1 FROM usuario WHERE email = ?", (email,)).fetchone(): flash("Este e-mail já está cadastrado.", "danger")
        else: session["cadastro"] = {"email": email, "senha": generate_password_hash(senha)}; return redirect(url_for("cadastro_complemento"))
    return render_template("auth/cadastro.html")

@app.route("/cadastro/complemento", methods=["GET", "POST"])
def cadastro_complemento():
    dados = session.get("cadastro")
    if not dados: return redirect(url_for("cadastro"))
    if request.method == "POST":
        nome, cpf, telefone, db = request.form.get("nome", "").strip(), somente_digitos(request.form.get("cpf", ""), 11), somente_digitos(request.form.get("telefone", ""), 11), get_db()
        if not nome or len(nome) > 150 or not cpf_valido(cpf) or db.execute("SELECT 1 FROM usuario WHERE cpf = ?", (cpf,)).fetchone(): flash("Nome obrigatório e CPF válido e único são necessários.", "danger")
        else:
            cursor = db.execute("INSERT INTO usuario (nome,email,senha,cpf,telefone) VALUES (?,?,?,?,?)", (nome, dados["email"], dados["senha"], cpf, telefone)); db.commit(); session.pop("cadastro"); session["user_id"] = cursor.lastrowid; return redirect(url_for("dashboard"))
    return render_template("auth/complemento.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_db().execute("SELECT * FROM usuario WHERE email = ?", (request.form.get("email", "").strip().lower(),)).fetchone()
        if user and check_password_hash(user["senha"], request.form.get("senha", "")): session.clear(); session["user_id"] = user["id"]; session["csrf"] = secrets.token_urlsafe(24); return redirect(url_for("dashboard"))
        flash("E-mail ou senha incorretos.", "danger")
    return render_template("auth/login.html")

@app.get("/sair")
def sair(): session.clear(); return redirect(url_for("login"))

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        user = get_db().execute("SELECT id FROM usuario WHERE email = ?", (request.form.get("email", "").strip().lower(),)).fetchone()
        if user:
            token, expira = secrets.token_urlsafe(32), datetime.utcnow() + timedelta(hours=1); get_db().execute("INSERT INTO recuperacao VALUES (?, ?, ?, 0)", (token, user["id"], expira.isoformat())); get_db().commit(); flash(f"Link de demonstração: {url_for('redefinir', token=token, _external=True)}", "info")
        else: flash("Se o e-mail existir, enviaremos as instruções.", "info")
    return render_template("auth/recuperar.html")

@app.route("/redefinir/<token>", methods=["GET", "POST"])
def redefinir(token):
    row = get_db().execute("SELECT * FROM recuperacao WHERE token = ? AND usado = 0", (token,)).fetchone()
    if not row or datetime.fromisoformat(row["expira_em"]) < datetime.utcnow(): flash("Token inválido ou expirado.", "danger"); return redirect(url_for("recuperar"))
    if request.method == "POST":
        senha = request.form.get("senha", "")
        if len(senha) < 8 or senha != request.form.get("confirmacao"): flash("As senhas devem ser iguais e ter 8 caracteres.", "danger")
        else:
            db = get_db(); db.execute("UPDATE usuario SET senha = ? WHERE id = ?", (generate_password_hash(senha), row["id"])); db.execute("UPDATE recuperacao SET usado = 1 WHERE token = ?", (token,)); db.commit(); flash("Senha redefinida.", "success"); return redirect(url_for("login"))
    return render_template("auth/redefinir.html")

@app.get("/dashboard")
@login_required
def dashboard():
    db = get_db()
    solicitacoes = db.execute("SELECT s.*, ea.nome escola_atual, ed.nome escola_desejada, se.nome serie FROM solicitacao s JOIN escola ea ON ea.id=s.id_escola_atual LEFT JOIN escola ed ON ed.id=s.id_escola_desejada JOIN serie se ON se.id=s.id_serie WHERE s.id_usuario_responsavel=? ORDER BY s.id DESC", (session["user_id"],)).fetchall()
    matches = db.execute("SELECT m.id, m.status FROM match_troca m JOIN solicitacao a ON a.id=m.id_solicitacao_a JOIN solicitacao b ON b.id=m.id_solicitacao_b WHERE (a.id_usuario_responsavel=? OR b.id_usuario_responsavel=?) AND m.status='ATIVO'", (session["user_id"], session["user_id"])).fetchall()
    return render_template("dashboard.html", solicitacoes=solicitacoes, matches=matches)

@app.get("/instrucoes")
@login_required
def instrucoes():
    return render_template("instrucoes.html")

def form_options():
    db = get_db(); return db.execute("SELECT * FROM ra ORDER BY nome").fetchall(), db.execute("SELECT * FROM serie ORDER BY id").fetchall(), db.execute("SELECT MIN(id) id, nome, id_ra FROM escola WHERE id_ra IS NOT NULL GROUP BY nome, id_ra ORDER BY nome").fetchall()

@app.get("/api/escolas")
def escolas_por_ra():
    ra_id = request.args.get("ra_id", type=int)
    if not ra_id: return jsonify([])
    escolas = get_db().execute("SELECT MIN(id) id, nome FROM escola WHERE id_ra=? GROUP BY nome ORDER BY nome", (ra_id,)).fetchall()
    return jsonify([dict(escola) for escola in escolas])

def validar_solicitacao(form):
    nome = form.get("nome", "").strip()
    if not nome or len(nome) > 150: raise ValueError("nome do aluno")
    try:
        serie = int(form["serie"]); escola_atual = int(form["escola_atual"]); ra_atual = int(form["ra_atual"]); ra_desejada = int(form["ra_desejada"]); escola_desejada = int(form["escola_desejada"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("selecione série, RA e escolas") from error
    db = get_db()
    if not db.execute("SELECT 1 FROM serie WHERE id=?", (serie,)).fetchone(): raise ValueError("série inválida")
    if not db.execute("SELECT 1 FROM escola WHERE id=? AND id_ra=?", (escola_atual, ra_atual)).fetchone(): raise ValueError("escola atual não pertence à RA selecionada")
    if not db.execute("SELECT 1 FROM escola WHERE id=? AND id_ra=?", (escola_desejada, ra_desejada)).fetchone(): raise ValueError("escola desejada não pertence à RA selecionada")
    turno_atual, turno_desejado = form.get("turno_atual", "").upper(), form.get("turno_desejado", "").upper()
    if turno_atual not in TURNOS or turno_desejado not in TURNOS: raise ValueError("turno inválido")
    if escola_atual == escola_desejada: raise ValueError("as escolas devem ser diferentes")
    motivo = form.get("motivo", "").strip()
    if len(motivo) > 2000: raise ValueError
    return nome, form.get("endereco", "").strip()[:255], serie, escola_atual, ra_desejada, escola_desejada, turno_atual, turno_desejado, motivo

def find_match(solicitacao_id):
    db, current = get_db(), get_db().execute("SELECT * FROM solicitacao WHERE id=?", (solicitacao_id,)).fetchone()
    candidate = db.execute("SELECT * FROM solicitacao WHERE id != ? AND status=? AND id_usuario_responsavel != ? AND id_serie=? AND id_escola_atual=? AND id_escola_desejada=? AND turno_atual=? AND turno_desejado=? LIMIT 1", (current["id"], STATUS_DISPONIVEL, current["id_usuario_responsavel"], current["id_serie"], current["id_escola_desejada"], current["id_escola_atual"], current["turno_desejado"], current["turno_atual"])).fetchone()
    if not candidate: return None
    now = datetime.utcnow().isoformat(); cur = db.execute("INSERT INTO match_troca (id_solicitacao_a,id_solicitacao_b,status,data_hora_criacao) VALUES (?,?,?,?)", (current["id"], candidate["id"], "ATIVO", now)); db.execute("UPDATE solicitacao SET status='EM_NEGOCIACAO', data_atualizacao=? WHERE id IN (?,?)", (now, current["id"], candidate["id"])); texto = "O sistema encontrou uma possível troca. Converse pelo chat e só conclua se os dois responsáveis estiverem de acordo. O Conecta Vagas apenas facilita o contato e não garante a troca ou a matrícula."; db.execute("INSERT INTO mensagem (id_match,mensagem,id_remetente,lida,tipo,data_hora_envio) VALUES (?,?,?,?,?,?)", (cur.lastrowid, texto, current["id_usuario_responsavel"], 0, "SISTEMA", now)); db.commit(); return cur.lastrowid

@app.route("/solicitacoes/nova", methods=["GET", "POST"])
@login_required
def nova_solicitacao():
    ras, series, escolas = form_options()
    if request.method == "POST":
        try:
            agora = datetime.utcnow().isoformat(); dados = validar_solicitacao(request.form)
            db = get_db(); cur = db.execute("INSERT INTO solicitacao (nome,endereco,id_serie,id_escola_atual,id_ra_desejada,id_escola_desejada,turno_atual,turno_desejado,id_usuario_responsavel,motivo_troca,status,data_criacao,data_atualizacao) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (*dados[:4], dados[4], dados[5], dados[6], dados[7], session["user_id"], dados[8], STATUS_DISPONIVEL, agora, agora)); db.commit(); match_id = find_match(cur.lastrowid); flash("Encontramos uma possível troca para você!" if match_id else "Solicitação criada. Agora ela está aguardando um match.", "success"); return redirect(url_for("detalhe_solicitacao", id=cur.lastrowid))
        except (KeyError, ValueError, sqlite3.IntegrityError) as error: flash(f"Revise os dados: {error}.", "danger")
    return render_template("solicitacoes/form.html", ras=ras, series=series, escolas=escolas, turnos=TURNOS, solicitacao=None)

@app.get("/solicitacoes/<int:id>")
@login_required
def detalhe_solicitacao(id):
    db = get_db(); item = db.execute("SELECT s.*, ea.nome escola_atual, ed.nome escola_desejada, se.nome serie, r.nome ra FROM solicitacao s JOIN escola ea ON ea.id=s.id_escola_atual LEFT JOIN escola ed ON ed.id=s.id_escola_desejada LEFT JOIN ra r ON r.id=s.id_ra_desejada JOIN serie se ON se.id=s.id_serie WHERE s.id=? AND s.id_usuario_responsavel=?", (id, session["user_id"])).fetchone()
    if not item: return "Solicitação não encontrada.", 404
    match = db.execute("SELECT * FROM match_troca WHERE (id_solicitacao_a=? OR id_solicitacao_b=?) AND status='ATIVO'", (id, id)).fetchone(); return render_template("solicitacoes/detalhe.html", item=item, match=match, ras=form_options()[0], series=form_options()[1], escolas=form_options()[2], turnos=TURNOS)

@app.route("/solicitacoes/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_solicitacao(id):
    db = get_db(); item = db.execute("SELECT s.*, ea.id_ra AS ra_atual FROM solicitacao s JOIN escola ea ON ea.id=s.id_escola_atual WHERE s.id=? AND s.id_usuario_responsavel=?", (id, session["user_id"])).fetchone()
    if not item: return "Solicitação não encontrada.", 404
    if item["status"] != STATUS_DISPONIVEL: flash("Só é possível editar uma solicitação aguardando match.", "warning"); return redirect(url_for("detalhe_solicitacao", id=id))
    if request.method == "POST":
        try:
            dados = validar_solicitacao(request.form); agora = datetime.utcnow().isoformat(); db.execute("UPDATE solicitacao SET nome=?, endereco=?, id_serie=?, id_escola_atual=?, id_ra_desejada=?, id_escola_desejada=?, turno_atual=?, turno_desejado=?, motivo_troca=?, data_atualizacao=? WHERE id=? AND id_usuario_responsavel=?", (*dados, agora, id, session["user_id"])); db.commit(); match_id = find_match(id); flash("Alterações salvas e match encontrado!" if match_id else "Alterações salvas.", "success"); return redirect(url_for("detalhe_solicitacao", id=id))
        except (KeyError, ValueError, sqlite3.IntegrityError) as error: flash(f"Revise os dados: {error}.", "danger")
    return render_template("solicitacoes/form.html", ras=form_options()[0], series=form_options()[1], escolas=form_options()[2], turnos=TURNOS, solicitacao=item)

@app.post("/solicitacoes/<int:id>/cancelar")
@login_required
def cancelar_solicitacao(id):
    db = get_db(); item = db.execute("SELECT * FROM solicitacao WHERE id=? AND id_usuario_responsavel=?", (id, session["user_id"])).fetchone()
    if not item: return "Solicitação não encontrada.", 404
    agora = datetime.utcnow().isoformat(); active = db.execute("SELECT * FROM match_troca WHERE (id_solicitacao_a=? OR id_solicitacao_b=?) AND status='ATIVO'", (id, id)).fetchone()
    db.execute("UPDATE solicitacao SET status='CANCELADA', data_atualizacao=? WHERE id=?", (agora, id))
    if active:
        other_id = active["id_solicitacao_b"] if active["id_solicitacao_a"] == id else active["id_solicitacao_a"]
        other = db.execute("SELECT * FROM solicitacao WHERE id=?", (other_id,)).fetchone(); db.execute("UPDATE solicitacao SET status=? WHERE id=? AND status='EM_NEGOCIACAO'", (STATUS_DISPONIVEL, other_id)); db.execute("UPDATE match_troca SET status='CANCELADO' WHERE id=?", (active["id"],)); db.execute("INSERT INTO mensagem (id_match,mensagem,id_remetente,lida,tipo,data_hora_envio) VALUES (?,?,?,?,?,?)", (active["id"], f"A solicitação de {item['nome']} foi cancelada pelo responsável. Esta troca foi cancelada.", session["user_id"], 0, "SISTEMA", agora)); enviar_email(other["id_usuario_responsavel"], "Troca cancelada", f"A troca envolvendo {item['nome']} foi cancelada.")
    db.commit(); flash("Solicitação cancelada.", "success"); return redirect(url_for("detalhe_solicitacao", id=id))

def user_match(match_id):
    return get_db().execute("SELECT m.*, a.nome aluno_a, b.nome aluno_b FROM match_troca m JOIN solicitacao a ON a.id=m.id_solicitacao_a JOIN solicitacao b ON b.id=m.id_solicitacao_b WHERE m.id=? AND (a.id_usuario_responsavel=? OR b.id_usuario_responsavel=?)", (match_id, session["user_id"], session["user_id"])).fetchone()

def enviar_email(usuario_id, assunto, corpo):
    destinatario = get_db().execute("SELECT email FROM usuario WHERE id=?", (usuario_id,)).fetchone()
    host = os.getenv("SMTP_HOST")
    if not destinatario or not host:
        app.logger.info("Notificação para usuario=%s | %s | %s", usuario_id, assunto, corpo)
        return
    mensagem = EmailMessage(); mensagem["Subject"] = assunto; mensagem["From"] = os.getenv("SMTP_FROM", "no-reply@conectavagas.local"); mensagem["To"] = destinatario["email"]; mensagem.set_content(corpo)
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as servidor:
        servidor.starttls(); servidor.login(os.getenv("SMTP_USER", ""), os.getenv("SMTP_PASSWORD", "")); servidor.send_message(mensagem)

@app.route("/matches/<int:id>", methods=["GET", "POST"])
@login_required
def match(id):
    item = user_match(id)
    if not item: return "Conversa não encontrada.", 404
    if request.method == "POST" and request.form.get("acao") in ("CANCELADO", "CONCLUIDO"):
        novo = request.form["acao"]
        db = get_db()
        agora = datetime.utcnow().isoformat()
        destino = "CONCLUIDA" if novo == "CONCLUIDO" else STATUS_DISPONIVEL
        db.execute("UPDATE match_troca SET status=? WHERE id=? AND status='ATIVO'", (novo, id))
        db.execute("UPDATE solicitacao SET status=? WHERE id IN (?,?) AND status='EM_NEGOCIACAO'", (destino, item["id_solicitacao_a"], item["id_solicitacao_b"]))
        if novo == "CANCELADO":
            db.execute("INSERT INTO mensagem (id_match,mensagem,id_remetente,lida,tipo,data_hora_envio) VALUES (?,?,?,?,?,?)", (id, "A conversa foi cancelada por um dos responsáveis. Esta troca foi cancelada.", session["user_id"], 0, "SISTEMA", agora))
        db.commit()
        flash("Conversa atualizada.", "success")
        return redirect(url_for("match", id=id))
    db = get_db(); db.execute("UPDATE mensagem SET lida=1 WHERE id_match=? AND id_remetente != ?", (id, session["user_id"])); db.commit(); mensagens = db.execute("SELECT m.*, u.nome remetente FROM mensagem m JOIN usuario u ON u.id=m.id_remetente WHERE m.id_match=? ORDER BY m.id", (id,)).fetchall(); return render_template("matches/detalhe.html", item=item, mensagens=mensagens)

@app.route("/matches/<int:id>/mensagens", methods=["GET", "POST"])
@login_required
def enviar_mensagem(id):
    item = user_match(id)
    if not item: return "Conversa não encontrada.", 404
    if request.method == "GET":
        mensagens = get_db().execute("SELECT m.id, m.mensagem, m.tipo, m.id_remetente, u.nome remetente FROM mensagem m JOIN usuario u ON u.id=m.id_remetente WHERE m.id_match=? ORDER BY m.id", (id,)).fetchall()
        return jsonify([dict(mensagem) for mensagem in mensagens])
    if item["status"] != "ATIVO": return "Conversa indisponível.", 403
    texto = request.form.get("mensagem", "").strip()
    if texto and len(texto) <= 2000: db = get_db(); db.execute("INSERT INTO mensagem (id_match,mensagem,id_remetente,lida,tipo,data_hora_envio) VALUES (?,?,?,?,?,?)", (id, texto, session["user_id"], 0, "USUARIO", datetime.utcnow().isoformat())); db.commit()
    return redirect(url_for("match", id=id) + "#chat")

@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        nome, cpf, telefone, endereco = request.form.get("nome", "").strip(), somente_digitos(request.form.get("cpf", ""), 11), somente_digitos(request.form.get("telefone", ""), 11), request.form.get("endereco", "").strip()
        outro_usuario = get_db().execute("SELECT 1 FROM usuario WHERE cpf=? AND id != ?", (cpf, session["user_id"])).fetchone()
        if not nome or len(nome) > 150 or not cpf_valido(cpf) or outro_usuario or len(endereco) > 255: flash("Revise o nome, CPF válido e único e endereço.", "danger")
        else:
            db = get_db(); db.execute("UPDATE usuario SET nome=?, cpf=?, telefone=?, endereco=? WHERE id=?", (nome, cpf, telefone, endereco, session["user_id"])); db.commit(); flash("Perfil atualizado.", "success")
    return render_template("perfil.html", user=get_db().execute("SELECT * FROM usuario WHERE id=?", (session["user_id"],)).fetchone())

with app.app_context(): init_db()