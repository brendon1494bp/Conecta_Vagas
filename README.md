 # Conecta Vagas

MVP monolítico em Flask para conectar responsáveis interessados em trocar escola e turno de alunos. A interface é mobile-first, usa Bootstrap apenas para componentes visuais e não utiliza Angular, Vue ou React.

## Roteiro executado

1. Validar requisitos, paleta e modelo relacional fornecidos.
2. Criar base Flask simples, com sessão, CSRF, hash de senha e dados de apoio.
3. Implementar cadastro em duas etapas, login, recuperação e perfil.
4. Implementar solicitações e `find_match`, com os critérios de escola, turno e série centralizados.
5. Implementar negociação, chat privado, recusa, conclusão e teste automatizado do caminho de matching.

## Executar

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Abra `http://127.0.0.1:5000`. O banco local `conecta_vagas.db` é criado automaticamente e recebe as séries, RAs e escolas dos scripts em `dados/`. Para produção, defina `SECRET_KEY` em um arquivo `.env` e configure o banco compatível com a infraestrutura do projeto. As notificações usam SMTP quando `SMTP_HOST`, `SMTP_USER` e `SMTP_PASSWORD` estão configurados; sem SMTP, ficam registradas no log da aplicação.

O schema de `dados/script_criacao_db.sql` foi complementado com endereço do usuário, status e datas da solicitação, turnos oficiais (`MATUTINO`, `VESPERTINO`, `NOTURNO`, `INTEGRAL`) e mensagens de sistema. A estrutura original de escolas, RAs, séries, matches e mensagens foi preservada.

## Testar

```text
python -m unittest discover -s tests -v
```

