import re
import tempfile
import unittest
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

    def create_request(self, current, desired, current_shift, desired_shift):
        data = {"csrf": self.token(), "nome": "Aluno de teste", "serie": 8, "ra_atual": 4 if current < 47 else 9, "escola_atual": current, "ra_desejada": 4 if desired < 47 else 9, "escola_desejada": desired, "turno_atual": current_shift, "turno_desejado": desired_shift}
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


if __name__ == "__main__":
    unittest.main()