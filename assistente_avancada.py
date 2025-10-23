# ... (cabeçalho, imports, SYSTEM_INSTRUCTION, e classe Hope __init__ e iniciar_nova_conversa mantidos) ...

    def chat(self, user_id, mensagem):
        if not self.inicializado:
            # Garante que o retorno seja um dicionário válido
            return {
                "resposta": "IA Inoperante devido a um erro de inicialização. Por favor, contate o administrador.",
                "links": {}
            }
        
        conversa = self.iniciar_nova_conversa(user_id)
        if not conversa:
             return {
                "resposta": "Não foi possível iniciar a conversa. Serviço indisponível.",
                "links": {}
            }

        try:
            response = conversa.send_message(mensagem)
            resposta_texto = response.text 
            # ... (extração de links) ...
            
            return {
                "resposta": resposta_texto,
                "links": {} # Retorno esperado
            }

        except APIError as e:
            logging.error(f"APIError ao chamar Gemini: {e}")
            return {
                "resposta": f"Desculpe, a comunicação com a IA falhou. Erro da API: {e}",
                "links": {} # Garante retorno válido
            }
        except Exception as e:
            logging.error(f"Erro inesperado no chat: {e}")
            return {
                "resposta": "Ocorreu um erro inesperado durante o processamento da sua mensagem.",
                "links": {} # Garante retorno válido
            }