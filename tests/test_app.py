import re
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from app import app, init_db


class ConectaVagasTest(unittest.TestCase):
    def setUp(self):
        self.database = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.database.close()
        app.config.update(TESTING=True, DATABASE=Path(self.database.name), SECRET_KEY="test-key")
        init_db()
        self.client = app.test_client()

    def tearDown(self):
        Path(self.database.name).unlink(missing_ok=True)

    def token(self):
        response = self.client.get("/login")
        return re.search(r'name="csrf" value="([^"]+)"', response.get_data(as_text=True)).group(1)

    def register(self, email, cpf, name):
        token = self.token()
        self.client.post("/cadastro", data={"csrf": token, "email": email, "senha": "senha-segura", "confirmacao": "senha-segura"})
        token = self.token()
        response = self.client.post("/cadastro/complemento", data={"csrf": token, "nome": name, "cpf": cpf})
        self.assertEqual(response.status_code, 302)

    def create_request(self, current, desired, current_shift, desired_shift, cep="70000000"):
        data = {"csrf": self.token(), "nome": "Aluno de teste", "cep": cep, "serie": 8, "ra_atual": 4 if current < 47 else 9, "escola_atual": current, "ra_desejada": 4 if desired < 47 else 9, "escola_desejada": desired, "turno_atual": current_shift, "turno_desejado": desired_shift}
        return self.client.post("/solicitacoes/nova", data=data)

    def test_inverse_requests_create_match(self):
        self.register("a@example.com", "52998224725", "Responsável A")
        first = self.create_request(1, 47, "MATUTINO", "VESPERTINO")
        self.assertEqual(first.status_code, 302)
        self.client.get("/sair")
        self.register("b@example.com", "16899535009", "Responsável B")
        second = self.create_request(47, 1, "VESPERTINO", "MATUTINO")
        self.assertEqual(second.status_code, 302)
        connection = __import__("sqlite3").connect(app.config["DATABASE"])
        row = connection.execute("SELECT status FROM match_troca").fetchone()
        connection.close()
        self.assertEqual(row[0], "ATIVO")

    def test_real_school_filter_and_edit_flow(self):
        self.register("c@example.com", "93541134780", "Responsável C")
        form = self.client.get("/solicitacoes/nova")
        self.assertEqual(form.status_code, 200)
        page = form.get_data(as_text=True)
        self.assertIn("Integral", page)
        self.assertIn("5º Ano - Ensino Fundamental I", page)
        schools = self.client.get("/api/escolas?ra_id=9")
        self.assertEqual(schools.status_code, 200)
        self.assertGreater(len(schools.get_json()), 1)
        created = self.create_request(1, 47, "MATUTINO", "MATUTINO")
        self.assertEqual(created.status_code, 302)
        detail = self.client.get("/solicitacoes/1")
        self.assertIn("Editar solicitação", detail.get_data(as_text=True))

    def test_request_can_be_created_without_cep(self):
        self.register("without-cep@example.com", "93541134780", "Responsável sem CEP")
        response = self.create_request(1, 47, "MATUTINO", "MATUTINO", cep="")
        self.assertEqual(response.status_code, 302)

    def test_request_match_polling_endpoint_reports_match_state(self):
        self.register("polling-a@example.com", "15350946056", "Responsável Polling A")
        self.create_request(1, 47, "MATUTINO", "VESPERTINO")
        response = self.client.get("/api/solicitacoes/1/match")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"matched": False, "match_id": None, "status": "AGUARDANDO_MATCH"})

        self.client.get("/sair")
        self.register("polling-b@example.com", "98765432100", "Responsável Polling B")
        self.create_request(47, 1, "VESPERTINO", "MATUTINO")
        self.client.get("/sair")
        self.client.post("/login", data={"csrf": self.token(), "email": "polling-a@example.com", "senha": "senha-segura"})
        response = self.client.get("/api/solicitacoes/1/match")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["matched"])
        self.assertEqual(response.get_json()["status"], "EM_NEGOCIACAO")

        self.client.get("/sair")
        self.register("polling-c@example.com", "93541134780", "Responsável Polling C")
        response = self.client.get("/api/solicitacoes/1/match")
        self.assertEqual(response.status_code, 404)

    def test_match_page_renders_for_participant(self):
        self.register("match-page-a@example.com", "93541134780", "Responsável Match A")
        self.create_request(1, 47, "MATUTINO", "VESPERTINO")
        self.client.get("/sair")
        self.register("match-page-b@example.com", "98765432100", "Responsável Match B")
        self.create_request(47, 1, "VESPERTINO", "MATUTINO")
        response = self.client.get("/matches/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Conversa privada", response.get_data(as_text=True))

    def test_authenticated_pages_have_collapsible_menu(self):
        self.register("menu@example.com", "15350946056", "Responsável Menu")
        response = self.client.get("/dashboard")
        page = response.get_data(as_text=True)
        self.assertIn('class="menu-toggle"', page)
        self.assertIn('aria-controls="main-menu"', page)
        self.assertIn('id="main-menu"', page)

    def test_pages_show_academic_demo_disclaimer(self):
        page = self.client.get("/login").get_data(as_text=True)
        self.assertIn("Versão demonstrativa para projeto acadêmico", page)

    def test_initial_route_discards_session_for_deleted_user(self):
        with self.client.session_transaction() as session:
            session["user_id"] = 9999
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/login")

    def test_protected_route_discards_session_for_deleted_user(self):
        with self.client.session_transaction() as session:
            session["user_id"] = 9999
        response = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    @patch.dict("os.environ", {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "no-reply@example.com",
        "SMTP_PASSWORD": "senha-de-teste",
        "SMTP_FROM": "",
        "SMTP_FROM_NAME": "Conecta Vagas",
    })
    @patch("app.smtplib.SMTP")
    def test_password_recovery_sends_reset_link_by_email(self, smtp_class):
        self.register("recovery@example.com", "15350946056", "Responsável Recuperação")
        smtp = smtp_class.return_value.__enter__.return_value
        response = self.client.post(
            "/recuperar",
            data={"csrf": self.token(), "email": "recovery@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Se o e-mail existir, enviaremos as instruções.", response.get_data(as_text=True))
        self.assertNotIn("demonstração", response.get_data(as_text=True))
        smtp.send_message.assert_called_once()
        mensagem = smtp.send_message.call_args.args[0]
        self.assertIn("no-reply@example.com", mensagem["From"])
        self.assertIn("/redefinir/", mensagem.get_content())

    @patch.dict("os.environ", {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "no-reply@example.com",
        "SMTP_PASSWORD": "senha-de-teste",
        "SMTP_FROM": "",
        "SMTP_FROM_NAME": "Conecta Vagas",
    })
    @patch("app.smtplib.SMTP")
    def test_password_recovery_accepts_new_password(self, smtp_class):
        self.register("reset@example.com", "16899535009", "Responsável Reset")
        self.client.post(
            "/recuperar",
            data={"csrf": self.token(), "email": "reset@example.com"},
        )
        connection = __import__("sqlite3").connect(app.config["DATABASE"])
        token = connection.execute("SELECT token FROM recuperacao").fetchone()[0]
        connection.close()
        response = self.client.post(
            f"/redefinir/{token}",
            data={"csrf": self.token(), "senha": "nova-senha-segura", "confirmacao": "nova-senha-segura"},
        )
        self.assertEqual(response.status_code, 302)
        self.client.get("/sair")
        response = self.client.post("/login", data={"csrf": self.token(), "email": "reset@example.com", "senha": "nova-senha-segura"})
        self.assertEqual(response.status_code, 302)

    def test_cancel_active_match_notifies_chat(self):
        self.register("d@example.com", "15350946056", "Responsável D")
        self.create_request(1, 47, "MATUTINO", "VESPERTINO")
        self.client.get("/sair")
        self.register("e@example.com", "98765432100", "Responsável E")
        self.create_request(47, 1, "VESPERTINO", "MATUTINO")
        token = self.token()
        response = self.client.post("/solicitacoes/2/cancelar", data={"csrf": token})
        self.assertEqual(response.status_code, 302)
        connection = __import__("sqlite3").connect(app.config["DATABASE"])
        status = connection.execute("SELECT status FROM match_troca").fetchone()[0]
        message = connection.execute("SELECT mensagem FROM mensagem WHERE tipo='SISTEMA' ORDER BY id DESC").fetchone()[0]
        connection.close()
        self.assertEqual(status, "CANCELADO")
        self.assertIn("cancelada", message)

    def test_invalid_cpf_is_rejected(self):
        token = self.token()
        self.client.post("/cadastro", data={"csrf": token, "email": "invalid@example.com", "senha": "senha-segura", "confirmacao": "senha-segura"})
        token = self.token()
        response = self.client.post("/cadastro/complemento", data={"csrf": token, "nome": "Responsável inválido", "cpf": "52998224726"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("CPF válido", response.get_data(as_text=True))

    def test_invalid_cpf_is_rejected_on_profile_edit(self):
        self.register("profile@example.com", "52998224725", "Responsável Perfil")
        response = self.client.post("/perfil", data={"csrf": self.token(), "nome": "Responsável Perfil", "cpf": "52998224726", "telefone": "", "endereco": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("CPF válido", response.get_data(as_text=True))

    def test_completed_match_can_be_evaluated_only_once(self):
        self.register("first@example.com", "52998224725", "Responsável Um")
        self.create_request(1, 47, "MATUTINO", "VESPERTINO")
        self.client.get("/sair")
        self.register("second@example.com", "16899535009", "Responsável Dois")
        self.create_request(47, 1, "VESPERTINO", "MATUTINO")
        response = self.client.post("/matches/1", data={"csrf": self.token(), "acao": "CONCLUIDO"})
        self.assertEqual(response.status_code, 302)
        response = self.client.post("/matches/1/avaliar", data={"csrf": self.token(), "nota": "5", "comentario": "Tudo certo"})
        self.assertEqual(response.status_code, 302)
        response = self.client.post("/matches/1/avaliar", data={"csrf": self.token(), "nota": "4"})
        self.assertEqual(response.status_code, 302)
        connection = __import__("sqlite3").connect(app.config["DATABASE"])
        count = connection.execute("SELECT COUNT(*) FROM avaliacao").fetchone()[0]
        statuses = connection.execute("SELECT status FROM solicitacao ORDER BY id").fetchall()
        connection.close()
        self.assertEqual(count, 1)
        self.assertEqual([row[0] for row in statuses], ["CONCLUIDA", "CONCLUIDA"])


if __name__ == "__main__":
    unittest.main()