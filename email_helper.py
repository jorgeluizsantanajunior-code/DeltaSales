import smtplib
from email.mime.text import MIMEText
import os

def enviar_email(destinatario_aluno):
    # Pegar os secrets configurados no Streamlit Cloud
    remetente = os.getenv("EMAIL")
    senha = os.getenv("SENHA_EMAIL")

    # Destinatários: aluno + professor
    destinatarios = [destinatario_aluno, "santanajr.prof@gmail.com"]

    # Assunto e corpo fixos
    assunto = "teste"
    corpo = "Teste"

    # Criar a mensagem
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)

    try:
        # Conexão segura com o SMTP do Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remetente, senha)
            servidor.sendmail(remetente, destinatarios, msg.as_string())
        print("E-mail enviado com sucesso.")
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
