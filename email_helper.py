import os
import smtplib
from email.mime.text import MIMEText
from dataclasses import dataclass
from typing import List
import unicodedata

# ---------------------------------
# Funções auxiliares
# ---------------------------------
def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def norm(s: str) -> str:
    return _strip_accents(s or "").lower().replace(" ", "")

def fmt(valor: float) -> str:
    s = f"{float(valor):,.0f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def shift_right(seq: List[float], k: int = 1) -> List[float]:
    return [0]*k + seq[:-k] if k > 0 else seq[:]

# ---------------------------------
# Parâmetros padrão
# ---------------------------------
@dataclass
class Params:
    pv: float = 4000
    pc: float = 2500
    descomp: float = 0.9
    jurcomp: float = 1.08
    transp: float = 500
    alserra: float = 10000
    alpraia: float = 50000
    movserra: float = 60000
    vuserra: float = 120
    movpraia: float = 100000
    vupraia: float = 120
    vendacart: float = 0.3
    vendaboleto: float = 0.4
    taxacart: float = 0.01
    taxainad: float = 0.1
    capital: float = 50000
    taxaesp: float = 0.15
    despmktfx: float = 5000
    despmktadc: float = 10000

# ---------------------------------
# Função que calcula demanda
# ---------------------------------
def calcular_demanda(local: str, marketing: str, recebimento: str) -> List[int]:
    loc = norm(local)
    mkt = norm(marketing)
    rec = norm(recebimento)

    base_vendas = [0.2, 0.4, 0.6] if loc == "serra" else [0.6, 0.7, 0.8]
    base_vendas = [x * 100 for x in base_vendas]

    fator_marketing = [1, 1.1, 1.1] if mkt == "conservador" else [1, 1.2, 1.2]
    fator_receb = 1.0 if rec == "avista" else 1.1 if rec == "cartao" else 1.15

    return [round(base_vendas[i] * fator_marketing[i] * fator_receb) for i in range(3)]

# ---------------------------------
# Função que gera o corpo do email
# ---------------------------------
def generate_email_body(nome, local, marketing, recebimento,
                        compra1pag, compra2pag, compra3pag,
                        compra1qnt, compra2qnt, compra3qnt,
                        params: Params = None) -> str:
    p = params or Params()
    loc = norm(local)
    mkt = norm(marketing)
    rec = norm(recebimento)

    demanda = calcular_demanda(local, marketing, recebimento)
    saldo = [max(0, compra1qnt - demanda[0])]
    saldo.append(max(0, saldo[0] + compra2qnt - demanda[1]))
    saldo.append(max(0, saldo[1] + compra3qnt - demanda[2]))

    venda = [
        compra1qnt if saldo[0] == 0 else demanda[0],
        saldo[0] + compra2qnt if saldo[1] == 0 else demanda[1],
        saldo[1] + compra3qnt if saldo[2] == 0 else demanda[2]
    ]
    receita = [p.pv * v for v in venda]

    def custo_unit(pag):
        return p.pc * p.descomp if norm(pag) == "adiantado" else p.pc if norm(pag) == "avista" else p.pc * p.jurcomp

    custounit = [custo_unit(compra1pag), custo_unit(compra2pag), custo_unit(compra3pag)]
    compras = [(custounit[i] + p.transp) * q for i, q in enumerate([compra1qnt, compra2qnt, compra3qnt])]
    estoque1 = (custounit[0] + p.transp) * saldo[0]
    estoque2 = ((estoque1 + compras[1]) / max(1, saldo[0] + compra2qnt)) * saldo[1] if saldo[0] + compra2qnt else 0
    estoque3 = ((estoque2 + compras[2]) / max(1, saldo[1] + compra2qnt)) * saldo[2] if saldo[1] + compra2qnt else 0

    if mkt == "agressivo":
        despmkt = [p.despmktfx + p.despmktadc, p.despmktfx, p.despmktfx]
    else:
        despmkt = [p.despmktfx] * 3

    # Só alguns exemplos de textos
    header = [f"Nome do aluno: {nome}", "Você escolheu as seguintes operações:", "", "Operações de Janeiro"]
    q11 = f"1. Em janeiro/20x1, foi integralizado o capital social no valor de R$ {fmt(p.capital)}"
    q12 = f"2. Em janeiro/20x1, foi pago R$ {fmt(p.alpraia if loc=='praiadocanto' else p.alserra)} de aluguel"
    q13 = f"3. Em janeiro/20x1, foi pago R$ {fmt(despmkt[0])} em marketing"

    return "\n".join(header + [q11, q12, q13])

# ---------------------------------
# Função de envio de e-mail
# ---------------------------------
def enviar_email(destinatario_aluno):
    # aqui você define os valores
    corpo = generate_email_body(
        nome="Maria Silva",
        local="Praia do Canto",
        marketing="Agressivo",
        recebimento="Boleto",
        compra1pag="À vista",
        compra2pag="Parcelado",
        compra3pag="Adiantado",
        compra1qnt=120,
        compra2qnt=150,
        compra3qnt=180
    )

    remetente = os.getenv("EMAIL")
    senha = os.getenv("SENHA_EMAIL")
    destinatarios = [destinatario_aluno, "santanajr.prof@gmail.com"]

    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = "Respostas da Atividade Competitiva"
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatarios, msg.as_string())
    print("E-mail enviado com sucesso.")

# ---------------------------------
# Teste local (descomente para rodar)
# enviar_email("aluno@example.com")
