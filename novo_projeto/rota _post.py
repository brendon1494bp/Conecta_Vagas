from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

app = FastAPI()
pwd = CryptContext(schemes=["bcrypt"])

class Login(BaseModel):
    email: EmailStr
    senha: str

@app.post("/login")
def login(dados: Login):
    if dados.email != "teste@email.com" or not pwd.verify(
        dados.senha,
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    ):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return {"mensagem": "Login realizado!", "usuario_id": 1}