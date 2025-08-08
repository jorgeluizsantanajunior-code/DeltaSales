import pandas as pd

# Função para salvar respostas no CSV
def salvar_csv(nome, email, local, marketing, recebimento, compra1qnt, compra1pag, compra2qnt, compra2pag, compra3qnt, compra3pag, resultado):
    # Criando um DataFrame com as respostas
    data = {
        "Nome": [nome],
        "E-mail": [email],
        "Local": [local],
        "Marketing": [marketing],
        "Recebimento": [recebimento],
        "Compra 1 Qtd": [compra1qnt],
        "Compra 1 Pag": [compra1pag],
        "Compra 2 Qtd": [compra2qnt],
        "Compra 2 Pag": [compra2pag],
        "Compra 3 Qtd": [compra3qnt],
        "Compra 3 Pag": [compra3pag],
        "Resultado": [resultado]
    }
    
    # Criando DataFrame
    df = pd.DataFrame(data)
    
    # Salvando no arquivo CSV (com opção de adicionar novas linhas)
    df.to_csv('respostas.csv', mode='a', header=False, index=False)
