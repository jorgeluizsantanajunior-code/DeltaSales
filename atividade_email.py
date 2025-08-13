
from dataclasses import dataclass
from typing import List, Tuple

# ---------------------------
# Helpers
# ---------------------------

def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def norm(s: str) -> str:
    """normalize to lowercase, remove spaces and accents"""
    s = s or ""
    s = _strip_accents(s)
    return s.lower().replace(" ", "")

def fmt(valor: float) -> str:
    """Format numbers as Brazilian currency-ish text without symbol, using . for thousands and , for decimals.
    We will keep 0 casas decimais to mirror the R example outputs where integers were printed.
    """
    try:
        n = float(valor)
    except Exception:
        return str(valor)
    s = f"{n:,.0f}"
    # US -> BR format
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def shift_right(seq: List[float], k: int = 1) -> List[float]:
    return [0]*k + seq[:-k] if k > 0 else seq[:]


# ---------------------------
# Parameters (defaults mirror the R file)
# ---------------------------

@dataclass
class Params:
    pv: float = 4000  # preço de venda à vista por produto
    pc: float = 2500  # preço de compra à vista por produto
    descomp: float = 0.9  # fator de desconto na compra (adiantado)
    jurcomp: float = 1.08  # fator de acréscimo na compra (parcelado)
    transp: float = 500  # transporte e impostos não recuperáveis por produto
    alserra: float = 10000  # aluguel da serra
    alpraia: float = 50000  # aluguel da praia do canto
    movserra: float = 60000  # móveis da serra (total)
    vuserra: float = 120  # vida útil (meses)
    movpraia: float = 100000  # móveis da praia do canto (total)
    vupraia: float = 120  # vida útil (meses)
    vendacart: float = 0.3  # % de vendas no cartão
    vendaboleto: float = 0.4  # % de vendas no boleto
    taxacart: float = 0.01  # taxa do cartão
    taxainad: float = 0.1  # taxa de inadimplência do boleto
    capital: float = 50000  # capital social
    taxaesp: float = 0.15  # juros do cheque especial
    despmktfx: float = 5000  # marketing fixo
    despmktadc: float = 10000  # adicional (agressivo)


# ---------------------------
# Core calculations
# ---------------------------

def calcular_demanda(local: str, marketing: str, recebimento: str) -> List[int]:
    loc = norm(local)
    mkt = norm(marketing)
    rec = norm(recebimento)

    # 1) Base por localização
    if loc == "serra":
        base_vendas = [0.2, 0.4, 0.6]
    else:  # "praiadocanto"
        base_vendas = [0.6, 0.7, 0.8]
    base_vendas = [x*100 for x in base_vendas]

    # 2) Fator marketing
    if mkt == "conservador":
        fator_marketing = [1, 1.1, 1.1]
    else:  # "agressivo"
        fator_marketing = [1, 1.2, 1.2]

    # 3) Fator recebimento
    if rec == "avista":
        fator_receb = 1.0
    elif rec == "cartao":
        fator_receb = 1.1
    else:  # "boleto"
        fator_receb = 1.15

    vendas_est = [round(base_vendas[i] * fator_marketing[i] * fator_receb) for i in range(3)]
    return vendas_est

def calcular_custos_unitarios(p: Params, compra1pag: str, compra2pag: str, compra3pag: str) -> List[float]:
    def custo(pag: str) -> float:
        pag = norm(pag)
        if pag == "adiantado":
            return p.pc * p.descomp
        elif pag == "avista":
            return p.pc
        else:  # parcelado
            return p.pc * p.jurcomp
    return [custo(compra1pag), custo(compra2pag), custo(compra3pag)]

def calcular_fluxo_caixa(p: Params, local: str, marketing: str, recebimento: str,
                         receita: List[float], pagamentos: List[float]) -> List[float]:
    loc = norm(local)
    mkt = norm(marketing)
    rec = norm(recebimento)

    if loc == "serra":
        caixa_local = [-(p.alserra + p.movserra/3)]*3
    else:
        caixa_local = [-(p.alpraia + p.movpraia/3)]*3

    if mkt == "conservador":
        caixa_marketing = [-p.despmktfx]*3
    else:  # agressivo
        caixa_marketing = [-(p.despmktfx+p.despmktadc), -p.despmktfx, -p.despmktfx]

    vendacart = p.vendacart
    vendaboleto = p.vendaboleto
    taxacart = p.taxacart
    taxainad = p.taxainad

    if rec == "avista":
        receb = receita[:]
    elif rec == "cartao":
        receb = [receita[i]*(1-vendacart) + shift_right([receita[j]*vendacart for j in range(3)])[i]*(1-taxacart) for i in range(3)]
    else:  # boleto
        part_cartao = shift_right([receita[j]*vendacart for j in range(3)])
        part_bol_1 = shift_right([receita[j]*vendaboleto/3 for j in range(3)])
        part_bol_2 = shift_right([receita[j]*vendaboleto/3 for j in range(3)], 2)

        receb = [
            receita[i]*(1-vendacart-vendaboleto)
            + part_cartao[i]*(1-taxacart)
            + part_bol_1[i]*(1-taxainad)
            + part_bol_2[i]*(1-taxainad)
            for i in range(3)
        ]

    fc = [caixa_local[i] + caixa_marketing[i] + receb[i] - pagamentos[i] for i in range(3)]
    return fc

# ---------------------------
# Public API
# ---------------------------

def generate_email_body(
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
    params: Params = None,
) -> str:
    """
    Retorna o corpo do e-mail (string) com:
      - cabeçalho com nome do aluno
      - subtítulos por mês
      - operações numeradas
    """
    import math

    p = params or Params()

    loc = norm(local)
    mkt = norm(marketing)
    rec = norm(recebimento)

    # --- Demanda e Vendas
    demanda = calcular_demanda(local, marketing, recebimento)

    saldo = [0, 0, 0]
    saldo[0] = max(0, compra1qnt - demanda[0])
    saldo[1] = max(0, saldo[0] + compra2qnt - demanda[1])
    saldo[2] = max(0, saldo[1] + compra3qnt - demanda[2])

    venda = [0, 0, 0]
    venda[0] = compra1qnt if saldo[0] == 0 else demanda[0]
    venda[1] = (saldo[0] + compra2qnt) if saldo[1] == 0 else demanda[1]
    venda[2] = (saldo[1] + compra3qnt) if saldo[2] == 0 else demanda[2]

    receita = [p.pv * v for v in venda]

    # --- Custos unitários e compras
    custounit = calcular_custos_unitarios(p, compra1pag, compra2pag, compra3pag)
    compras = [(custounit[i] + p.transp) * q for i, q in enumerate([compra1qnt, compra2qnt, compra3qnt])]

    # Estoques e CMV (replicando as fórmulas do R)
    estoque1 = (custounit[0] + p.transp) * saldo[0]
    # Nota: replicando literalmente a lógica do R, inclusive a possível repetição de compra2qnt na base de março
    estoque2 = ((estoque1 + compras[1]) / max(1, (saldo[0] + compra2qnt))) * saldo[1] if (saldo[0] + compra2qnt) != 0 else 0
    estoque3 = ((estoque2 + compras[2]) / max(1, (saldo[1] + compra2qnt))) * saldo[2] if (saldo[1] + compra2qnt) != 0 else 0
    cmv = [compras[0] - estoque1, estoque1 + compras[1] - estoque2, estoque2 + compras[2] - estoque3]

    # Despesas
    if loc == "serra":
        aluguel = [p.alserra]*3
        deprec = [p.movserra/p.vuserra]*3
    else:
        aluguel = [p.alpraia]*3
        deprec = [p.movpraia/p.vupraia]*3

    # Cartão (não usado diretamente nos textos, mas calculado como no R)
    despcartao = [0, 0, 0]
    if rec in ("cartao", "boleto"):
        despcartao = [r*p.vendacart*p.taxacart for r in receita]

    # Recebimentos a prazo
    vendacart = p.vendacart
    vendaboleto = p.vendaboleto
    taxacart = p.taxacart
    taxainad = p.taxainad

    cartaoreceb = [
        receita[i]*(1-vendacart) + shift_right([receita[j]*vendacart for j in range(3)])[i]*(1-taxacart)
        for i in range(3)
    ]

    boletoreceb = [
        receita[i]*(1-vendacart-vendaboleto)
        + shift_right([receita[j]*vendacart for j in range(3)])[i]*(1-taxacart)
        + shift_right([receita[j]*vendaboleto/3 for j in range(3)])[i]*(1-taxainad)
        + shift_right([receita[j]*vendaboleto/3 for j in range(3)], 2)[i]*(1-taxainad)
        for i in range(3)
    ]

    # Pagamentos (fornecedor)
    qnts = [compra1qnt, compra2qnt, compra3qnt]

    pagavista = [q*p.pc for q in qnts]
    for i, pag in enumerate([compra1pag, compra2pag, compra3pag]):
        if norm(pag) != "avista":
            pagavista[i] = 0

    pagadiant = [q*p.pc*p.descomp for q in qnts]
    for i, pag in enumerate([compra1pag, compra2pag, compra3pag]):
        if norm(pag) != "adiantado":
            pagadiant[i] = 0
    # desloca para frente (pago antes)
    pagadiant = [pagadiant[1], pagadiant[2], 0]

    pagparc_total = [q*p.pc*p.jurcomp for q in qnts]
    for i, pag in enumerate([compra1pag, compra2pag, compra3pag]):
        if norm(pag) != "parcelado":
            pagparc_total[i] = 0
    pagparc = [0, 0, 0]
    # duas últimas parcelas nos dois meses seguintes ao mês da compra
    third = [x/3 for x in pagparc_total]
    # mês 2 recebe 1/3 do mês 1 + 1/3 do mês 2 (se parcelado), mês 3 idem + 1/3 do mês 3
    pagparc = [
        0 + 0,
        third[0] + third[1],
        third[0] + third[1] + third[2],
    ]

    pagamentos = [pagavista[i] + pagadiant[i] + pagparc[i] + p.transp*qnts[i] for i in range(3)]

    # Fluxo de caixa e cheque especial (como no R)
    fc = calcular_fluxo_caixa(p, local, marketing, recebimento, receita, pagamentos)

    despfin = [0, 0, 0]
    caixa = [0, 0, 0]
    caixa[0] = p.capital + fc[0]
    if caixa[0] < 0:
        despfin[0] = caixa[0]*p.taxaesp
        caixa[0] = caixa[0]*(1+p.taxaesp)
    caixa[1] = caixa[0] + fc[1]
    if caixa[1] < 0:
        despfin[1] = caixa[1]*p.taxaesp
        caixa[1] = caixa[1]*(1+p.taxaesp)
    caixa[2] = caixa[1] + fc[2]
    if caixa[2] < 0:
        despfin[2] = caixa[2]*p.taxaesp
        caixa[2] = caixa[2]*(1+p.taxaesp)

    # Despesa de marketing por mês (usada no texto do mês 1 dependendo da estratégia)
    despmkt = [0, 0, 0]
    if mkt == "agressivo":
        despmkt = [p.despmktfx + p.despmktadc, p.despmktfx, p.despmktfx]
    else:
        despmkt = [p.despmktfx, p.despmktfx, p.despmktfx]

    # ---------------------------
    # Montagem dos textos (q11..q37 do R)
    # ---------------------------

    # Janeiro
    q11 = f"Em janeiro/20x1, foi integralizado, por meio de depósito em conta bancária, o capital social no valor de R$ {fmt(p.capital)}"
    q12 = f"Em janeiro/20x1, foi pago o valor mensal de R$ {fmt(p.alpraia if loc=='praiadocanto' else p.alserra)} referente ao direito de uso do imóvel em janeiro/20x1."
    q13 = ("Em janeiro/20x1, foi pago o valor mensal de R$ "
           f"{fmt(despmkt[0])} referente a gastos com marketing.")
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
               else f" Além disso, sabe-se que a administradora do cartão de crédito cobra uma taxa de {p.taxacart*100:.0f}% pelas vendas no cartão"
               if rec=="cartao"
               else f" Além disso, sabe-se que a administradora do cartão de crédito cobra uma taxa de {p.taxacart*100:.0f}% pelas vendas no cartão e que há um risco de inandimplência de {p.taxainad*100:.0f}% para o saldo de contas a receber no boleto.")
    q16 = (f"Em janeiro/20x1, foram vendidos {venda[0]} pacotes do café civeta totalizando R$ {fmt(receita[0])}. "
           f"Sendo {rec16}.{extra16}")
    q17 = (f"Em janeiro/20x1 foi pago o valor de R$ "
           f"{fmt(round((p.movpraia if loc=='praiadocanto' else p.movserra)/3))} referente à primeira parcela dos móveis adquiridos.")
    q18 = (f"Em janeiro/20x1 foi adiantado ao fornecedor o valor de R$ {fmt(compra2qnt*p.pc*p.descomp)} referente a produtos ainda não entregues."
           if norm(compra2pag)=="adiantado" else "")

    # Fevereiro
    q21 = (f"Em fevereiro/20x1, foi pago o valor mensal de R$ {fmt(p.alpraia if loc=='praiadocanto' else p.alserra)} referente ao direito de uso do imóvel em fevereiro/20x1.")
    q22 = (f"Em fevereiro/20x1, foi pago o valor mensal de R$ {fmt(p.despmktfx)} referente a gastos com marketing.")
    q23 = ("" if rec=="avista"
           else f"Em fevereiro/20x1, foi recebido o valor R$ {fmt(receita[0]*p.vendacart*(1-p.taxacart))}, referente às vendas no cartão de crédito do mês anterior."
           if rec=="cartao"
           else f"Em fevereiro/20x1, foi recebido o valor R$ {fmt(receita[0]*p.vendacart*(1-p.taxacart))}, referente às vendas no cartão de crédito do mês anterior e R$ {fmt(receita[0]*p.vendaboleto*(1-p.taxainad)/3)} referente às vendas no boleto do mês anterior.")
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
    q28 = (f"Em fevereiro/20x1 foi pago ao fornecedor o valor de R$ {fmt((p.pc*p.jurcomp*compra1qnt)/3)} referente a mercadorias anteriormente entregues."
           if norm(compra1pag)=="parcelado" else "")

    # Março
    q31 = (f"Em março/20x1, foi pago o valor mensal de R$ {fmt(p.alpraia if loc=='praiadocanto' else p.alserra)} referente ao direito de uso do imóvel em março/20x1.")
    q32 = (f"Em março/20x1, foi pago o valor mensal de R$ {fmt(p.despmktfx)} referente a gastos com marketing.")
    q33 = ("" if rec=="avista"
           else f"Em março/20x1, foi recebido o valor R$ {fmt(receita[1]*p.vendacart*(1-p.taxacart))}, referente às vendas no cartão de crédito do mês anterior."
           if rec=="cartao"
           else f"Em março/20x1, foi recebido o valor R$ {fmt(receita[1]*p.vendacart*(1-p.taxacart))}, referente às vendas no cartão de crédito do mês anterior e R$ {fmt(receita[0]*p.vendaboleto*(1-p.taxainad)/3 + receita[1]*p.vendaboleto*(1-p.taxainad)/3)} referente às vendas no boleto dos meses anteriores.")
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
    q37 = (f"Em março/20x1 foi pago ao fornecedor o valor de R$ {fmt((p.pc*p.jurcomp*compra1qnt)/3 + (p.pc*p.jurcomp*compra2qnt)/3 if norm(compra2pag)=='parcelado' else (p.pc*p.jurcomp*compra1qnt)/3)} referente a mercadorias anteriormente entregues."
           if (norm(compra1pag)=="parcelado" or norm(compra2pag)=="parcelado") else "")

    # Coletar, filtrar vazios e numerar
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
