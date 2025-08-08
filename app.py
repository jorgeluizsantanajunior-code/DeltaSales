import streamlit as st

# Função para formatar valores
def fmt(x):
    return format(x, ",.2f")

# Definindo variáveis fixas do jogo
local = st.selectbox("Escolha a localização", ["Serra", "Praia do Canto"])
marketing = st.selectbox("Escolha a estratégia de marketing", ["Conservador", "Agressivo"])
recebimento = st.selectbox("Escolha a política de recebimento", ["À vista", "Cartão", "Boleto"])

# Variáveis de compras (quantidade e forma de pagamento)
compra1qnt = st.number_input("Quantidade de compras no Mês 1", min_value=0, value=100)
compra1pag = st.selectbox("Forma de pagamento para Mês 1", ["À vista", "Parcelado", "Adiantado"])

compra2qnt = st.number_input("Quantidade de compras no Mês 2", min_value=0, value=100)
compra2pag = st.selectbox("Forma de pagamento para Mês 2", ["À vista", "Parcelado", "Adiantado"])

compra3qnt = st.number_input("Quantidade de compras no Mês 3", min_value=0, value=100)
compra3pag = st.selectbox("Forma de pagamento para Mês 3", ["À vista", "Parcelado", "Adiantado"])

# Coletando nome e e-mail do aluno
nome = st.text_input("Nome do aluno")
email = st.text_input("E-mail do aluno")

# Se o botão "Enviar" for pressionado
if st.button("Enviar escolhas"):
    if nome and email:
        # Processamento das escolhas
        # Colocar aqui os cálculos e lógica do código original (baseado no código R)
        resultado = f"""
        Resultados:
        Localização: {local}
        Estratégia de Marketing: {marketing}
        Política de Recebimento: {recebimento}
        Compras Mês 1: {compra1qnt} pacotes, forma de pagamento {compra1pag}
        Compras Mês 2: {compra2qnt} pacotes, forma de pagamento {compra2pag}
        Compras Mês 3: {compra3qnt} pacotes, forma de pagamento {compra3pag}
        """
        
        # Exibir resultado no app
        st.write(resultado)

    else:
        st.error("Por favor, insira seu nome e e-mail para enviar as escolhas.")
