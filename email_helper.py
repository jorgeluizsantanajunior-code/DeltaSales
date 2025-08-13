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
    q11 = f"Em janeiro/20x1, foi integralizado, por meio de depósito em conta bancária, o capital social no valor de R$ {fmt(p.capital)}"
    q12 = f"Em janeiro/20x1, foi pago o valor mensal de R$ {fmt(p.alpraia if loc=='praiadocanto' else p.alserra)} referente ao direito de uso do imóvel em janeiro/20x1."
    q13 = f"Em janeiro/20x1, foi pago o valor mensal de R$ {fmt(despmkt[0])} referente a gastos com marketing."
    q14 = ("Em janeiro/20x1, foram adquiridos móveis com vida útil de 10 anos no valor total de R$ "
           f"{fmt(p.movpraia if loc=='praiadocanto' else p.movserra)} a serem pagos em 3 parcelas mensais com vencimento no fim de cada mês iniciando em janeiro de 20x1.")
    val15 = (p.pc*compra1qnt if norm(compra1pag)=="avista"
             else p.pc*p.jurcomp*compra1qnt if norm(compra1pag)=="parcelado"
             else p.pc*p.descomp*compra1qnt)
    pag15 = ("à vista" if norm(compra1pag)=="avista"
             else "parcelado em 3 parcelas mensais" if norm(compra1pag)=="parcelado"
             else "adiantado")
    q15 = (f"Em janeiro/20x1, foram adquiridos {compra1qnt} pacotes do café civeta sendo R$ {fmt(val15)} {pag15} "
           f"e R$ {fmt(compra1qnt*p.transp)} pagos à vista pelos custos de transporte e impostos de importação não recuperáveis.")
    rec16 = ("todo o valor recebido à vista" if rec=="avista"
             else "70% recebido à vista e 30% no cartão de crédito a ser recebido no mês subsequente" if rec=="cartao"
             else "30% recebido à vista, 30% no cartão de crédito e 40% no boleto parcelado em 3x sem juros")
    extra16 = ("" if rec=="avista"
               else f" Além disso, sabe-se que a administradora do cartão de crédito cobra uma taxa de {Params.taxacart*100:.0f}% pelas vendas no cartão"
               if rec=="cartao"
               else f" Além disso, sabe-se que a administradora do cartão de crédito cobra uma taxa de {Params.taxacart*100:.0f}% pelas vendas no cartão e que há um risco de inandimplência de {Params.taxainad*100:.0f}% para o saldo de contas a receber no boleto.")
    q16 = (f"Em janeiro/20x1, foram vendidos {venda[0]} pacotes do café civeta totalizando R$ {fmt(receita[0])}. "
           f"Sendo {rec16}.{extra16}")
    q17 = (f"Em janeiro/20x1 foi pago o valor de R$ "
           f"{fmt(round((p.movpraia if loc=='praiadocanto' else p.movserra)/3))} referente à primeira parcela dos móveis adquiridos.")
    q18 = (f"Em janeiro/20x1 foi adiantado ao fornecedor o valor de R$ {fmt(compra2qnt*p.pc*p.descomp)} referente a produtos ainda não entregues."
           if norm(compra2pag)=="adiantado" else "")

    # Fevereiro
    q21 = (f"Em fevereiro/20x1, foi pago o valor mensal de R$ {fmt(p.alpraia if loc=='praiadocanto' else p.alserra)} referente ao direito de uso do imóvel em fevereiro/20x1.")
    q22 = (f"Em fevereiro/20x1, foi pago o valor mensal de R$ {fmt(Params.despmktfx)} referente a gastos com marketing.")
    q23 = ("" if rec=="avista"
           else f"Em fevereiro/20x1, foi recebido o valor R$ {fmt(receita[0]*Params.vendacart*(1-Params.taxacart))}, referente às vendas no cartão de crédito do mês anterior."
           if rec=="cartao"
           else f"Em fevereiro/20x1, foi recebido o valor R$ {fmt(receita[0]*Params.vendacart*(1-Params.taxacart))}, referente às vendas no cartão de crédito do mês anterior e R$ {fmt(receita[0]*Params.vendaboleto*(1-Params.taxainad)/3)} referente às vendas no boleto do mês anterior.")
    val24 = (p.pc*compra2qnt if norm(compra2pag)=="avista"
             else p.pc*p.jurcomp*compra2qnt if norm(compra2pag)=="parcelado"
             else p.pc*p.descomp*compra2qnt)
    pag24 = ("à vista" if norm(compra2pag)=="avista"
             else "parcelado em 3 parcelas mensais" if norm(compra2pag)=="parcelado"
             else "abatido de adiantamento feito no mês anterior")
    q24 = (f"Em fevereiro/20x1, foram adquiridos {compra2qnt} pacotes do café civeta sendo R$ {fmt(val24)} {pag24} "
           f"e R$ {fmt(compra2qnt*p.transp)} pagos à vista pelos custos de transporte e impostos de importação não recuperáveis.")
    q25 = (f"Em fevereiro/20x1, foram vendidos {venda[1]} pacotes do café civeta totalizando R$ {fmt(receita[1])}. "
           f"Sendo {rec16}.{extra16}")
    q26 = (f"Em fevereiro/20x1 foi pago o valor de R$ "
           f"{fmt(round((p.movpraia if loc=='praiadocanto' else p.movserra)/3))} referente à segunda parcela dos móveis adquiridos.")
    q27 = (f"Em fevereiro/20x1 foi adiantado ao fornecedor o valor de R$ {fmt(compra3qnt*p.pc*p.descomp)} referente a produtos ainda não entregues."
           if norm(compra3pag)=="adiantado" else "")
    q28 = (f"Em fevereiro/20x1 foi pago ao fornecedor o valor de R$ {fmt((Params.pc*Params.jurcomp*compra1qnt)/3)} referente a mercadorias anteriormente entregues."
           if norm(compra1pag)=="parcelado" else "")

    # Março
    q31 = (f"Em março/20x1, foi pago o valor mensal de R$ {fmt(p.alpraia if loc=='praiadocanto' else p.alserra)} referente ao direito de uso do imóvel em março/20x1.")
    q32 = (f"Em março/20x1, foi pago o valor mensal de R$ {fmt(Params.despmktfx)} referente a gastos com marketing.")
    q33 = ("" if rec=="avista"
           else f"Em março/20x1, foi recebido o valor R$ {fmt(receita[1]*Params.vendacart*(1-Params.taxacart))}, referente às vendas no cartão de crédito do mês anterior."
           if rec=="cartao"
           else f"Em março/20x1, foi recebido o valor R$ {fmt(receita[1]*Params.vendacart*(1-Params.taxacart))}, referente às vendas no cartão de crédito do mês anterior e R$ {fmt(receita[0]*Params.vendaboleto*(1-Params.taxainad)/3 + receita[1]*Params.vendaboleto*(1-Params.taxainad)/3)} referente às vendas no boleto dos meses anteriores.")
    val34 = (p.pc*compra3qnt if norm(compra3pag)=="avista"
             else p.pc*p.jurcomp*compra3qnt if norm(compra3pag)=="parcelado"
             else p.pc*p.descomp*compra3qnt)
    pag34 = ("à vista" if norm(compra3pag)=="avista"
             else "parcelado em 3 parcelas mensais" if norm(compra3pag)=="parcelado"
             else "abatido de adiantamento feito no mês anterior")
    q34 = (f"Em março/20x1, foram adquiridos {compra3qnt} pacotes do café civeta sendo R$ {fmt(val34)} {pag34} "
           f"e R$ {fmt(compra3qnt*p.transp)} pagos à vista pelos custos de transporte e impostos de importação não recuperáveis.")
    q35 = (f"Em março/20x1, foram vendidos {venda[2]} pacotes do café civeta totalizando R$ {fmt(receita[2])}. "
           f"Sendo {rec16}.{extra16}")
    q36 = (f"Em março/20x1 foi pago o valor de R$ "
           f"{fmt(round((p.movpraia if loc=='praiadocanto' else p.movserra)/3))} referente à terceira parcela dos móveis adquiridos.")
    q37 = (f"Em março/20x1 foi pago ao fornecedor o valor de R$ {fmt((Params.pc*Params.jurcomp*compra1qnt)/3 + (Params.pc*Params.jurcomp*compra2qnt)/3 if norm(compra2pag)=='parcelado' else (Params.pc*Params.jurcomp*compra1qnt)/3)} referente a mercadorias anteriormente entregues."
           if (norm(compra1pag)=="parcelado" or norm(compra2pag)=="parcelado") else "")

    # Coletar, filtrar vazios e numerar com seções
    jan = [q11, q12, q13, q14, q15, q16, q17, q18]
    fev = [q21, q22, q23, q24, q25, q26, q27, q28]
    mar = [q31, q32, q33, q34, q35, q36, q37]

    def enumerate_ops(items: List[str], start_idx: int) -> Tuple[List[str], int]:
        out = []
        idx = start_idx
        for it in items:
            if it and it.strip():
                out.append(f"{idx}. {it.strip()}")
                idx += 1
        return out, idx

    header = [f"Nome do aluno: {nome}", "Você escolheu as seguintes operações:"]

    body_lines = header[:]
    n = 1
    body_lines.append("")
    body_lines.append("Operações de Janeiro")
    ops, n = enumerate_ops(jan, n); body_lines.extend(ops)

    body_lines.append("")
    body_lines.append("Operações de Fevereiro")
    ops, n = enumerate_ops(fev, n); body_lines.extend(ops)

    body_lines.append("")
    body_lines.append("Operações de Março")
    ops, n = enumerate_ops(mar, n); body_lines.extend(ops)

    return "\n".join(body_lines)

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
