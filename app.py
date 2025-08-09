import streamlit as st
import pandas as pd

# Criando os dados da tabela (agora com as localizações como colunas)
dados = {
    "Categoria": [
        "Aluguel Mensal",
        "Investimento em Móveis",
        "Vida Útil dos Móveis (anos)",
        "Condições de Pagamento dos Móveis",
        "Fatia de Mercado no Mês 1",
        "Fatia de Mercado no Mês 2",
        "Fatia de Mercado no Mês 3"
    ],
    "Serra": [
        "R$ 5.000", "R$ 60.000", 10, "Parcelado em 12 vezes", "20%", "40%", "60%"
    ],
    "Praia do Canto": [
        "R$ 20.000", "R$ 100.000", 10, "Parcelado em 12 vezes", "60%", "70%", "80%"
    ]
}

# Criando um DataFrame
tabela = pd.DataFrame(dados)

tabela = tabela.set_index("Categoria")

# Função para formatar valores
def fmt(x):
    return format(x, ",.2f")

# Seção de Contexto
def mostrar_contexto():
  
    st.image("pagina1.png", caption="", use_container_width=True)
    
    st.title("Bem-vindo à atividade da Civeta Nobre Importações!")
    
    st.subheader("Sobre a empresa")
    st.write("""
    A empresa **Civeta Nobre Importações** está sendo criada com o objetivo de comercializar o famoso café civeta, 
    conhecido por seu processo único de produção na Indonésia. A empresa estabeleceu um contato direto com um fornecedor 
    no país asiático e tem acesso a um preço competitivo de importação. Nessa parte da atividade, seu objetivo será tomar
    decisões que resultem na maximização do lucro líquido da empresa nos seus três primeiros meses de funcinamento.
    """)
    
    st.subheader("O Produto")
    st.write("""
    O café será vendido exclusivamente em pacotes de 1kg, voltados para clientes de alto poder aquisitivo e cafeterias 
    especializadas localizadas em **Vitória, Espírito Santo**.
    """)
    
    st.subheader("Estudo de Mercado")
    st.write("""
    Após uma análise de mercado, a Civeta Nobre concluiu que, se conseguisse atingir todo o público potencial da cidade, 
    teria capacidade de vender até 100 pacotes por mês, com um preço de R\$ 4.000 por pacote (1kg). Esse número representa o 
    limite máximo de mercado em Vitória, considerando o perfil e a demanda do público local.
    """)
    st.write("""
    A velocidade com que a empresa atingirá esse mercado dependerá de algumas decisões estratégicas importantes,
    sendo elas: (1) a localização, (2) a campanha de marketing e (3) a política de recebimentos dos clientes.
    """)
    st.write("""
    Além disso, a empresa poderá obter descontos do fornecedor, dependendo da forma que irá pagar os produtos
    e é livre para comprar a quantidade de pacotes desejada. Contudo, a empresa possui uma quantia limitada
    de recursos próprios, pois o capital integralizado pelos sócios no início do negócio é de apenas R\$ 50.000
    (depositado em conta bancária).
    """)
    st.write("""
    Embora a quantidade de pacotes a serem comprados seja ilimitada, se a empresa gastar mais recursos do caixa do que possui,
    sua conta bancária entra automaticamente em cheque especial e estará sujeita à taxa de juros da instituição financeira.
    """)
    
    st.subheader("Localização da empresa")
    st.write("""
    A empresa precisa escolher entre duas localizações para sua operação física. A Serra oferece um aluguel mais barato e um
    investimento em móveis mais acessível, mas está afastada do centro, o que pode limitar o acesso ao público. A Praia do Canto, por outro lado,
    possui um aluguel mais caro e um investimento maior em móveis, mas oferece uma localização nobre, próxima ao público-alvo, o que irá atrair mais clientes.
    """)
    # Exibindo a tabela no Streamlit
    st.write("**Tabela de Dados da Localização e Mercado**", tabela)
    st.write("""
    Obs.: A primeira parcela dos móveis é paga em janeiro e do aluguel são pagas em janeiro. Ou seja, o aluguel é pago no mesmo mês em que é utilizado.
    """)
    
    st.subheader("Estratégia de Marketing")
    st.write("""
    A empresa está considerando duas estratégias de marketing. A Campanha Conservadora envolve um gasto fixo mensal de R\$ 5.000,
    com a gestão das redes sociais sendo feita por uma empresa terceirizada, focando em divulgação digital orgânica.
    Com essa campanha, espera-se que a demanda esperada **a partir da localização escolhida** seja 10% maior no mês de fevereiro e
    no mês de março.
    """)
    st.write("""
    Outra opção seria a Campanha Agressiva. Nessa campanha, além do gasto fixo mensal de R\$ 5.000 e a empresa arcaria com um pagamento
    de R\$ 50.000 no primeiro mês, para impulsionamento e parcerias com influenciadores locais. Com essa estratégia, espera-se que a demanda esperada
    **a partir da localização** escolhida seja 20% maior no mês de fevereiro e no mês de março.
    """)
    
    st.subheader("Política de Recebimento dos Clientes")
    st.write("""
    A empresa considera três políticas de vendas. Os efeitos dessas políticas são calculados
    a partir das expectativas de demandas das escolhas anteriores (localização e marketing).
    """)
    st.write("""
    **1) Apenas à vista:** essa alternativa não altera as expectativas de vendas e não envolve custos adicionais.
    """)
    st.write("""
    **2) À vista e no cartão de crédito:** essa alternativa produz um aumento de 10% na demanda de cada mês (após considerar escolhas de localização e marketing). A venda no
    no cartão de crédito é de apenas 1x. Ou seja, todo o valor vendido é inteiramente recebido no mês seguinte,
    e a administradora do cartão garante o pagamento. Contudo, ela cobra uma taxa de 1% sobre as vendas no cartão e
    é sabido que, do total vendido em cada mês, 30% corresponderão às vendas no cartão de crédito e o restante (70%) à vista.
    """)
    st.write("""
    **3) À vista, crédito e boleto:** essa alternativa produz um aumento de 15% na demanda de cada mês (após considerar escolhas de localização e marketing). As condições de venda no cartão
    de crédito são as mesmas da opção "À vista e no cartão de crédito". Já as vendas no boleto serão, todas elas, parceladas em
    3 parcelas mensais, sendo a primeira recebido 1 mês após a venda. É sabido que há um risco de que 10% do saldo de contas a receber das vendas no boleto não sejam recebidos e
    que, do total vendido em cada mês, 30% corresponderão às vendas no cartão de crédito, 40% às vendas no boleto e o restante,
    (30%) à vista.
    """)
    
    st.subheader("Aquisião dos produtos")
    st.write("""
    Os pacotes do café civeta são adquiridos mensalmente estando disponíveis para atender a demanda do mês em que são
    adquiridos.
    **Negociação com fornecedor**: O preço negociado com o fornecedor da Indonésia é R\$ 2.500 por pacote se for à vista, R\$ 2.250 por pacote
    se for pago 30 dias antes do envio e R\$ 2.700 por pacote se for parcelado em 3 parcelas (primeira parcela vencendo 1 mês após a compra).
    Como a empresa inicia em janeiro, a compra de janeiro não pode ser adiantada. Caso opte por adiantar a mercadoria enviada em fevereiro,
    o valor pago por ela terá efeito no caixa de janeiro.
    """)
    st.write("""
    **Custos adicionais**: Além do preço negociado com fornecedor, a empresa precisa arcar com custos de importação (transporte e impostos não recuperáveis)
    que correspondem a R\$ 500 por pacote e são sempre pagos à vista, no mês de envio das mercadorias. Por exemplo, se a mercadoria
    de fevereiro é adquirida por adiantamento, o efeito no pagamento ao fornecedor ocorre em janeiro, mas o efeito dos custos de importação
    ocorrem em fevereiro. O mesmo vale para o parcelamento. Apenas a quantia referente ao fornecedor é parcelada, os demais custos são sempre à vista.
    """)
    
    st.subheader("Cheque especial e outras informações")
    st.write("""
    Os gestores possuem liberdade para comprar a quantidade que desejar. Contudo, não possui recursos próprios infinitos. Ao gastar
    mais do que possui em caixa, a empresa estará utilizando recursos do cheque especial, que está sujeito a uma taxa de juros de 15% ao mês.
    """)
    st.write("""
    Para todas as operações, os dias são irrelevantes. Ou seja, embora capital próprio seja de R\$ 50.000, o budget de janeiro é
    R\$ 50.000 mais aos acrescimos de caixa decorrente das operações de janeiro. Portanto, o tempo é apenas relevante ao passar de um mês
    para outro. Sendo assim, a taxa de juros do cheque especial é calculada sobre o saldo negativo do mês em que o caixa estiver negativo,
    e incorporada a esse saldo. Ou seja, se ao final de janeiro o caixa fechar em -10.000 antes dos juros, o saldo final do caixa de janeiro
    após o juros será de -11.500. O mesmo para os demais meses.
    """)
    st.write("""
    Similarmente, a depreciação dos móveis leva em consideração os três meses completos.
    """)
    
    st.write("""
    Com base nas informações acima, tome as decisões que **MAXIMIZAM O LUCRO DO PRIMEIRO TRIMESTRE** da Civeta Nobre Importações.
    """)
    

# Seção de Escolhas do Usuário
def mostrar_escolhas():
    # Definindo variáveis fixas do jogo
    local = st.selectbox("Escolha a localização", ["Serra", "Praia do Canto"])
    marketing = st.selectbox("Escolha a estratégia de marketing", ["Conservador", "Agressivo"])
    recebimento = st.selectbox("Escolha a política de recebimento", ["À vista", "Cartão", "Boleto"])

    compra1qnt = st.number_input("Quantidade de compras no Mês 1", min_value=0, value=100)
    compra1pag = st.selectbox("Forma de pagamento para Mês 1", ["À vista", "Parcelado", "Adiantado"])

    compra2qnt = st.number_input("Quantidade de compras no Mês 2", min_value=0, value=100)
    compra2pag = st.selectbox("Forma de pagamento para Mês 2", ["À vista", "Parcelado", "Adiantado"])

    compra3qnt = st.number_input("Quantidade de compras no Mês 3", min_value=0, value=100)
    compra3pag = st.selectbox("Forma de pagamento para Mês 3", ["À vista", "Parcelado", "Adiantado"])

    nome = st.text_input("Nome do(s) aluno(s)")
    email = st.text_input("E-mail do aluno (apenas 1 email)")

    if st.button("Enviar escolhas"):
        if nome and email:
            resultado = f"""
            Resultados:
            Localização: {local}
            Estratégia de Marketing: {marketing}
            Política de Recebimento: {recebimento}
            Compras Mês 1: {compra1qnt} pacotes, forma de pagamento {compra1pag}
            Compras Mês 2: {compra2qnt} pacotes, forma de pagamento {compra2pag}
            Compras Mês 3: {compra3qnt} pacotes, forma de pagamento {compra3pag}
            """
            
            st.write(resultado)
            st.success("As suas escolhas foram registradas!")
        else:
            st.error("Por favor, insira seu nome e e-mail para enviar as escolhas.")

# Função principal com navegação por botões
def main():
    # Exibe a seção de contexto
    mostrar_contexto()

    # Botão "Próximo" para ir para a próxima seção
    if st.button("Tomar Decisões"):
        # Exibe a seção de escolhas
        mostrar_escolhas()

if __name__ == "__main__":
    main()