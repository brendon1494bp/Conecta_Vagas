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

Abra `http://127.0.0.1:8000`. O banco local `conecta_vagas.db` é criado automaticamente pelo schema SQLite de desenvolvimento e recebe as séries, RAs e escolas dos scripts em `dados/`. Para produção, crie o banco MySQL executando `dados/script_criacao_db.sql`, carregue os scripts de inserção e defina `DATABASE_URL=mysql://usuario:senha@host:3306/conecta_vagas` e `SECRET_KEY` em um arquivo `.env`. Nunca versione o `.env`. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_NAME` e `SMTP_FROM` para habilitar o envio real de recuperação de senha e notificações. Para Gmail, use uma senha de aplicativo, nunca a senha principal da conta.

O schema de `dados/script_criacao_db.sql` foi complementado com endereço do usuário, status e datas da solicitação, turnos oficiais (`MATUTINO`, `VESPERTINO`, `NOTURNO`, `INTEGRAL`) e mensagens de sistema. A estrutura original de escolas, RAs, séries, matches e mensagens foi preservada.

## Testar

```text
python -m unittest discover -s tests -v
```

