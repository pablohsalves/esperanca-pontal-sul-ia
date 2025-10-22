# dados_biblicos.py

import random

def carregar_versiculos(nome_arquivo="versiculos.txt"):
    """
    Função para carregar os versículos de um arquivo de texto.

    Args:
        nome_arquivo (str): O nome do arquivo contendo os versículos (um por linha).

    Returns:
        list: Uma lista contendo todos os versículos lidos.
    """
    try:
        # 'r' é para leitura (read), 'encoding="utf-8"' é bom para caracteres especiais
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            # strip() remove espaços em branco e quebras de linha no início/fim de cada linha
            versiculos = [linha.strip() for linha in arquivo if linha.strip()]
        return versiculos
    except FileNotFoundError:
        print(f"ERRO: Arquivo de versículos '{nome_arquivo}' não encontrado.")
        return []

def versiculo_aleatorio(lista_versiculos):
    """
    Seleciona e retorna um versículo aleatório da lista.

    Args:
        lista_versiculos (list): A lista de versículos carregados.

    Returns:
        str: Um versículo bíblico aleatório ou uma mensagem de erro.
    """
    if not lista_versiculos:
        return "Desculpe, a lista de versículos está vazia."
    
    # random.choice() é uma função do módulo 'random' que escolhe um item da lista
    return random.choice(lista_versiculos)

# Dicionário de respostas comuns para o nosso modelo de IA simples
RESPOSTAS_COMUNS = {
    "horario": "Os horários de culto são: Domingo às 10h e Quarta-feira às 20h. Venha nos visitar!",
    "endereco": "Nossa igreja fica na Rua da Fé, nº 123, Bairro Esperança. Esperamos por você!",
    "doacao": "Você pode fazer uma doação via PIX (chave: igreja@fe.org) ou diretamente na secretaria da igreja.",
    "batismo": "Para agendar o seu batismo, por favor, envie um email para batismo@fe.org ou procure um dos pastores após o culto.",
    "pastor": "O nosso pastor principal é o Pastor João da Graça. Ele está disponível para aconselhamento às terças e quintas-feiras."
}