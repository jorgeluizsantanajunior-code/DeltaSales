# email_helper.py
import os
import smtplib
from typing import Optional
from email.mime.text import MIMEText

from atividade_email import generate_email_body, Params


def gerar_corpo_email(
    nome: str,
    local: str,
    marketing: str,
    recebimento: str,
    compra1pag: str,
    compra2pag: str,
    compra3pag: str,
    compra1qnt: int,
    compra2qnt: int,
    compra3qnt: int,
    params: Optional[Params] = None,
) -> str:
    """
    Gera o corpo do e-mail com cabeçalho, subtítulos (Jan/Fev/Mar) e
    operações numeradas (pulando as que não se aplicam).
    """
    return generate_email_body(
        nome=nome,
        local=local,           # "Serra" ou "Praia do Canto" (acentos ok)
        marketing=marketing,   # "Conservador" ou "Agressivo"
        recebimento=recebimento,  # "À vista", "Cartão" ou "Boleto"
        compra1pag=compra1pag, # "Adiantado", "À vista" ou "Parcelado"
        compra2pag=compra2pag,
        compra3pag=compra3pag,
        compra1qnt=compra1qnt,
        compra2qnt=compra2qnt,
        compra3qnt=compra3qnt,
        params=params,
    )


def enviar_email(
    destinatario_aluno: str,
    corpo: str,
    assunto: str = "Respostas da Atividade Competitiva",
) -> None:
    """
    Envia o e-mail para o aluno (em cópia o professor) com o corpo já pronto.
    Requer as variáveis de ambiente EMAIL e SENHA_EMAIL.
    """
    remetente = os.getenv("EMAIL")
    senha = os.getenv("SENHA_EMAIL")

    if not remetente or not senha:
        raise RuntimeError(
            "Variáveis de ambiente EMAIL e/ou SENHA_EMAIL não configuradas no ambiente."
        )

    destinatarios = [destinatario_aluno, "santanajr.prof@gmail.com"]

    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatarios, msg.as_string())
