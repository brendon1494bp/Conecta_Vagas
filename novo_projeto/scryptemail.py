import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg['Subject'] = 'Teste'
msg['From'] = 'brendonpedro390@gmail.com'
msg['To'] = 'brendon1494.bp@gmail.com'
msg.set_content('Teste de envio.')

# Usando SMTP e starttls() na porta 587
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()  # Ativa criptografia TLS
    smtp.login('brendonpedro390@gmail.com', 'br&ndon14b')
    smtp.send_message(msg)

print("Email enviado com sucesso!")