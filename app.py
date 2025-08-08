import streamlit as st

# Função para formatar valores
def fmt(x):
    return format(x, ",.2f")

# Seção de Contexto
def mostrar_contexto():
  
    st.image("pagina1.jpg", caption="Bem-vindo à atividade da Civeta Nobre Importações!", use_column_width=True)
    
    st.subheader("Sobre a empresa")
    st.write("""
    A empresa **Civeta Nobre Importações** está sendo criada com o objetivo de comercializar o famoso café civeta, 
    conhecido por seu processo único de produção na Indonésia. A empresa estabeleceu um contato direto com um fornecedor 
    no país asiático e tem acesso a um preço competitivo de importação.
    """)
    
    st.subheader("O Produto")
    st.write("""
    O café será vendido exclusivamente em pacotes de 1kg, voltados para clientes de alto poder aquisitivo e cafeterias 
    especializadas localizadas em **Vitória, Espírito Santo**.
    """)
    
    st.subheader("Estudo de Mercado")
    st.write("""
    Após uma análise de mercado, a Civeta Nobre concluiu que, se conseguisse atingir todo o público potencial da cidade, 
    teria capacidade de vender até 100 pacotes por mês, com um preço de R$ 4.000 por pacote (1kg). Esse número representa o 
    limite máximo de mercado em Vitória, considerando o perfil e a demanda do público local.
    """)
    
    st.write("""
    Agora, você vai tomar algumas decisões estratégicas para essa empresa e ajudar a modelar os resultados dela.
    """)
    
    st.button("Próximo")  # Aqui você pode incluir um botão para seguir para a próxima seção.

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

    nome = st.text_input("Nome do aluno")
    email = st.text_input("E-mail do aluno")

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

# Função principal que vai decidir qual página mostrar
def main():
    page = st.selectbox("Escolha uma opção", ["Contexto", "Fazer Escolhas"])

    if page == "Contexto":
        mostrar_contexto()
    else:
        mostrar_escolhas()

# Executando a função principal
if __name__ == "__main__":
    main()
