import smtplib
from email.mime.text import MIMEText
from atividade_email import generate_email_body, Params
import os

def enviar_email(destinatario_aluno, nome_aluno,
                 local, marketing, recebimento,
                 compra1pag, compra2pag, compra3pag,
                 compra1qnt, compra2qnt, compra3qnt):
   
    # (se quiser, personalize parâmetros padrão passando Params(...))
    corpo = generate_email_body(
        nome=nome_aluno,
        local=local,                  # "serra" ou "praia do canto" (qualquer caixa; acentos são aceitos)
        marketing=marketing,          # "conservador" ou "agressivo"
        recebimento=recebimento,      # "à vista", "cartão" ou "boleto"
        compra1pag=compra1pag,        # "adiantado", "à vista" ou "parcelado"
        compra2pag=compra2pag,
        compra3pag=compra3pag,
        compra1qnt=compra1qnt,
        compra2qnt=compra2qnt,
        compra3qnt=compra3qnt,
        # params=Params(...)  # opcional: para alterar preços, taxas, etc.
    )
    
    # Pegar os secrets configurados no Streamlit Cloud
    remetente = os.getenv("EMAIL")
    senha = os.getenv("SENHA_EMAIL")

    # Destinatários: aluno + professor
    destinatarios = [destinatario_aluno, "santanajr.prof@gmail.com"]

    # Assunto e corpo fixos
    assunto = "Respostas da Atividade Competitiva"
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
