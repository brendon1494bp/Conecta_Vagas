from flask import Flask, request, jsonify

app = Flask(__name__)


# =========================
# DADOS
# =========================

usuarios = [
    {
        "id": 1,
        "nome": "João da Silva",
        "email": "joao@email.com",
        "telefone": "61999999999",
        "senha": "123456"
    }
]

alunos = [
    {
        "id": 1,
        "nome": "Pedro da Silva",
        "escola": "Escola 01",
        "turno": "Matutino",
        "serie": "5º Ano",
        "ra": "123456"
    }
]

escolas = [
    {
        "id": 1,
        "nome": "Escola Classe 01",
        "ra": "Plano Piloto"
    },
    {
        "id": 2,
        "nome": "Centro Educacional 01",
        "ra": "Plano Piloto"
    },
    {
        "id": 3,
        "nome": "Escola Classe 10",
        "ra": "Taguatinga"
    },
    {
        "id": 4,
        "nome": "Centro Educacional 05",
        "ra": "Ceilândia"
    }
]

vagas = [
    {
        "id": 1,
        "escola_id": 1,
        "serie": "5º Ano",
        "turno": "Matutino",
        "quantidade": 10
    },
    {
        "id": 2,
        "escola_id": 2,
        "serie": "6º Ano",
        "turno": "Vespertino",
        "quantidade": 5
    }
]

solicitacoes = []


# =========================
# USUÁRIOS / RESPONSÁVEIS
# =========================

@app.route('/usuarios', methods=['POST'])
def criar_usuario():

    dados = request.get_json()

    novo_usuario = {
        "id": len(usuarios) + 1,
        "nome": dados.get("nome"),
        "email": dados.get("email"),
        "telefone": dados.get("telefone"),
        "senha": dados.get("senha")
    }

    usuarios.append(novo_usuario)

    return jsonify(novo_usuario), 201


@app.route('/usuarios', methods=['GET'])
def listar_usuarios():

    return jsonify(usuarios), 200


@app.route('/usuarios/<int:id>', methods=['GET'])
def buscar_usuario(id):

    usuario = next(
        (u for u in usuarios if u["id"] == id),
        None
    )

    if usuario is None:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 404

    return jsonify(usuario), 200


@app.route('/usuarios/<int:id>', methods=['PUT'])
def editar_usuario(id):

    usuario = next(
        (u for u in usuarios if u["id"] == id),
        None
    )

    if usuario is None:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 404

    dados = request.get_json()

    usuario["nome"] = dados.get("nome", usuario["nome"])
    usuario["email"] = dados.get("email", usuario["email"])
    usuario["telefone"] = dados.get("telefone", usuario["telefone"])
    usuario["senha"] = dados.get("senha", usuario["senha"])

    return jsonify(usuario), 200


@app.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):

    usuario = next(
        (u for u in usuarios if u["id"] == id),
        None
    )

    if usuario is None:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 404

    usuarios.remove(usuario)

    return jsonify({
        "mensagem": "Usuário excluído com sucesso"
    }), 200


# =========================
# ALUNOS
# =========================

@app.route('/alunos', methods=['POST'])
def criar_aluno():

    dados = request.get_json()

    novo_aluno = {
        "id": len(alunos) + 1,
        "nome": dados.get("nome"),
        "escola": dados.get("escola"),
        "turno": dados.get("turno"),
        "serie": dados.get("serie"),
        "ra": dados.get("ra")
    }

    alunos.append(novo_aluno)

    return jsonify(novo_aluno), 201


@app.route('/alunos', methods=['GET'])
def listar_alunos():

    return jsonify(alunos), 200


@app.route('/alunos/<int:id>', methods=['GET'])
def buscar_aluno(id):

    aluno = next(
        (a for a in alunos if a["id"] == id),
        None
    )

    if aluno is None:
        return jsonify({
            "erro": "Aluno não encontrado"
        }), 404

    return jsonify(aluno), 200


@app.route('/alunos/<int:id>', methods=['PUT'])
def editar_aluno(id):

    aluno = next(
        (a for a in alunos if a["id"] == id),
        None
    )

    if aluno is None:
        return jsonify({
            "erro": "Aluno não encontrado"
        }), 404

    dados = request.get_json()

    aluno["nome"] = dados.get("nome", aluno["nome"])
    aluno["escola"] = dados.get("escola", aluno["escola"])
    aluno["turno"] = dados.get("turno", aluno["turno"])
    aluno["serie"] = dados.get("serie", aluno["serie"])
    aluno["ra"] = dados.get("ra", aluno["ra"])

    return jsonify(aluno), 200


@app.route('/alunos/<int:id>', methods=['DELETE'])
def deletar_aluno(id):

    aluno = next(
        (a for a in alunos if a["id"] == id),
        None
    )

    if aluno is None:
        return jsonify({
            "erro": "Aluno não encontrado"
        }), 404

    alunos.remove(aluno)

    return jsonify({
        "mensagem": "Aluno excluído com sucesso"
    }), 200


# =========================
# ESCOLAS
# =========================

@app.route('/escolas', methods=['POST'])
def criar_escola():

    dados = request.get_json()

    nova_escola = {
        "id": len(escolas) + 1,
        "nome": dados.get("nome"),
        "ra": dados.get("ra")
    }

    escolas.append(nova_escola)

    return jsonify(nova_escola), 201


@app.route('/escolas', methods=['GET'])
def listar_escolas():

    return jsonify(escolas), 200


@app.route('/escolas/<int:id>', methods=['GET'])
def buscar_escola(id):

    escola = next(
        (e for e in escolas if e["id"] == id),
        None
    )

    if escola is None:
        return jsonify({
            "erro": "Escola não encontrada"
        }), 404

    return jsonify(escola), 200


@app.route('/escolas/<int:id>', methods=['PUT'])
def editar_escola(id):

    escola = next(
        (e for e in escolas if e["id"] == id),
        None
    )

    if escola is None:
        return jsonify({
            "erro": "Escola não encontrada"
        }), 404

    dados = request.get_json()

    escola["nome"] = dados.get("nome", escola["nome"])
    escola["ra"] = dados.get("ra", escola["ra"])

    return jsonify(escola), 200


@app.route('/escolas/<int:id>', methods=['DELETE'])
def deletar_escola(id):

    escola = next(
        (e for e in escolas if e["id"] == id),
        None
    )

    if escola is None:
        return jsonify({
            "erro": "Escola não encontrada"
        }), 404

    escolas.remove(escola)

    return jsonify({
        "mensagem": "Escola excluída com sucesso"
    }), 200


# =========================
# BUSCAR ESCOLAS POR RA
# =========================

@app.route('/escolas/ra', methods=['POST'])
def buscar_escolas_por_ra():

    dados = request.get_json()

    ra = dados.get("ra")

    resultado = [
        escola
        for escola in escolas
        if escola["ra"] == ra
    ]

    return jsonify(resultado), 200


# =========================
# VAGAS
# =========================

@app.route('/vagas', methods=['POST'])
def criar_vaga():

    dados = request.get_json()

    nova_vaga = {
        "id": len(vagas) + 1,
        "escola_id": dados.get("escola_id"),
        "serie": dados.get("serie"),
        "turno": dados.get("turno"),
        "quantidade": dados.get("quantidade")
    }

    vagas.append(nova_vaga)

    return jsonify(nova_vaga), 201


@app.route('/vagas', methods=['GET'])
def listar_vagas():

    return jsonify(vagas), 200


@app.route('/vagas/<int:id>', methods=['GET'])
def buscar_vaga(id):

    vaga = next(
        (v for v in vagas if v["id"] == id),
        None
    )

    if vaga is None:
        return jsonify({
            "erro": "Vaga não encontrada"
        }), 404

    return jsonify(vaga), 200


@app.route('/vagas/<int:id>', methods=['PUT'])
def editar_vaga(id):

    vaga = next(
        (v for v in vagas if v["id"] == id),
        None
    )

    if vaga is None:
        return jsonify({
            "erro": "Vaga não encontrada"
        }), 404

    dados = request.get_json()

    vaga["escola_id"] = dados.get(
        "escola_id",
        vaga["escola_id"]
    )

    vaga["serie"] = dados.get(
        "serie",
        vaga["serie"]
    )

    vaga["turno"] = dados.get(
        "turno",
        vaga["turno"]
    )

    vaga["quantidade"] = dados.get(
        "quantidade",
        vaga["quantidade"]
    )

    return jsonify(vaga), 200


@app.route('/vagas/<int:id>', methods=['DELETE'])
def deletar_vaga(id):

    vaga = next(
        (v for v in vagas if v["id"] == id),
        None
    )

    if vaga is None:
        return jsonify({
            "erro": "Vaga não encontrada"
        }), 404

    vagas.remove(vaga)

    return jsonify({
        "mensagem": "Vaga excluída com sucesso"
    }), 200


# =========================
# SOLICITAÇÕES
# =========================

@app.route('/solicitacoes', methods=['POST'])
def criar_solicitacao():

    dados = request.get_json()

    nova_solicitacao = {
        "id": len(solicitacoes) + 1,
        "responsavel_id": dados.get("responsavel_id"),
        "aluno_id": dados.get("aluno_id"),
        "vaga_id": dados.get("vaga_id"),
        "status": "Pendente"
    }

    solicitacoes.append(nova_solicitacao)

    return jsonify(nova_solicitacao), 201


@app.route('/solicitacoes', methods=['GET'])
def listar_solicitacoes():

    return jsonify(solicitacoes), 200


@app.route('/solicitacoes/<int:id>', methods=['GET'])
def buscar_solicitacao(id):

    solicitacao = next(
        (s for s in solicitacoes if s["id"] == id),
        None
    )

    if solicitacao is None:
        return jsonify({
            "erro": "Solicitação não encontrada"
        }), 404

    return jsonify(solicitacao), 200


@app.route('/solicitacoes/<int:id>', methods=['PUT'])
def editar_solicitacao(id):

    solicitacao = next(
        (s for s in solicitacoes if s["id"] == id),
        None
    )

    if solicitacao is None:
        return jsonify({
            "erro": "Solicitação não encontrada"
        }), 404

    dados = request.get_json()

    solicitacao["responsavel_id"] = dados.get(
        "responsavel_id",
        solicitacao["responsavel_id"]
    )

    solicitacao["aluno_id"] = dados.get(
        "aluno_id",
        solicitacao["aluno_id"]
    )

    solicitacao["vaga_id"] = dados.get(
        "vaga_id",
        solicitacao["vaga_id"]
    )

    solicitacao["status"] = dados.get(
        "status",
        solicitacao["status"]
    )

    return jsonify(solicitacao), 200


@app.route('/solicitacoes/<int:id>', methods=['DELETE'])
def deletar_solicitacao(id):

    solicitacao = next(
        (s for s in solicitacoes if s["id"] == id),
        None
    )

    if solicitacao is None:
        return jsonify({
            "erro": "Solicitação não encontrada"
        }), 404

    solicitacoes.remove(solicitacao)

    return jsonify({
        "mensagem": "Solicitação excluída com sucesso"
    }), 200


# =========================
# INICIAR SERVIDOR
# =========================

if __name__ == '__main__':
    app.run(debug=True)
