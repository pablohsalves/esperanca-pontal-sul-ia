# assistente.py

from dados_biblicos import carregar_versiculos, versiculo_aleatorio, RESPOSTAS_COMUNS

class ParceiroDeFe:
    """
    Classe principal que simula a assistente de atendimento da igreja.
    """
    def __init__(self):
        """Inicializa a assistente carregando os versículos bíblicos."""
        # Carrega a lista de versículos uma vez que a assistente é criada
        self.versiculos = carregar_versiculos()
        print("Assistente Parceiro de Fé inicializada e versículos carregados.")

    def obter_resposta(self, pergunta):
        """
        Processa a pergunta do usuário e retorna a resposta mais adequada.
        
        Args:
            pergunta (str): A pergunta do usuário.

        Returns:
            str: A resposta da assistente.
        """
        # Limpa a pergunta e a transforma em minúsculas para facilitar a busca
        pergunta_limpa = pergunta.lower().strip()
        
        # --- Lógica de Busca de Resposta Comum (Busca por Palavra-Chave) ---
        
        # Iteramos sobre as chaves (palavras-chave como "horario", "endereco")
        for palavra_chave, resposta in RESPOSTAS_COMUNS.items():
            if palavra_chave in pergunta_limpa:
                return resposta

        # --- Lógica de Versículo Bíblico ---
        
        # Se o usuário pedir um versículo
        if "versiculo" in pergunta_limpa or "bíblia" in pergunta_limpa:
            vers = versiculo_aleatorio(self.versiculos)
            return f"Claro! Aqui está uma Palavra para o seu coração:\n\n{vers}"
        
        # --- Resposta Padrão ---
        
        # Se nenhuma palavra-chave for encontrada
        return "Desculpe, não entendi a sua pergunta. Você gostaria de saber sobre: 'horário', 'endereço', 'doação', 'batismo' ou um 'versículo'?"

    def enviar_saudacao(self):
        """Retorna uma saudação inicial."""
        return "Olá! Bem-vindo(a) à nossa igreja. Eu sou o Parceiro de Fé, sua assistente virtual. Em que posso ajudar hoje?"


# --- Bloco de Teste/Execução (main.py) ---
# Você pode rodar este arquivo para testar a assistente no terminal.
if __name__ == "__main__":
    
    # 1. Cria a instância da assistente
    assistente = ParceiroDeFe()
    print("-" * 30)

    # 2. Envia a saudação
    print(assistente.enviar_saudacao())

    # 3. Loop de conversação
    while True:
        # Pede a entrada do usuário
        entrada = input("\nVocê: ")
        
        # Condição de saída
        if entrada.lower() in ["sair", "tchau", "fim"]:
            print("Parceiro de Fé: Que Deus te abençoe! Até logo.")
            break
            
        # Obtém e exibe a resposta
        resposta = assistente.obter_resposta(entrada)
        print(f"Parceiro de Fé: {resposta}")