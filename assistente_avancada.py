# assistente_avancada.py - Versão V32.1 (Máxima Robustez na Leitura da Chave)

import os
import json
import logging
from dotenv import load_dotenv # Importa o dotenv para leitura local
from google import genai
from google.genai.errors import APIError

# Tenta carregar variáveis de ambiente do arquivo .env (apenas para teste local)
load_dotenv() 

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# --- CONFIGURAÇÃO CRÍTICA DA CHAVE ---
# O Render garante que 'GEMINI_API_KEY' está no os.environ
# O load_dotenv garante que, localmente, ele leia do arquivo .env
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# --------------------------------------

# Definição do modelo
MODEL_NAME = "gemini-2.5-flash"

class Hope:
    def __init__(self, nome_assistente="Hope"):
        self.nome_assistente = nome_assistente
        self.client = None
        self.conversas = {} # Para rastrear histórico
        self.inicializado = False
        
        # TENTA INICIALIZAR O CLIENTE GEMINI
        if GEMINI_API_KEY:
            try:
                # CRÍTICO: Inicializa o cliente com a chave.
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.inicializado = True
                logging.info(f"Assistente '{self.nome_assistente}' inicializado com sucesso.")
            except Exception as e:
                # Falha na inicialização por erro na chave/rede
                logging.error(f"ERRO CRÍTICO: Falha ao inicializar o cliente Gemini com a chave: {e}")
                self.inicializado = False
        else:
            # Falha se a chave não foi encontrada 
            logging.error("ERRO CRÍTICO: GEMINI_API_KEY não encontrada no ambiente. Verifique o Render ou o arquivo .env.")
            self.inicializado = False

    def iniciar_nova_conversa(self, user_id, historico=None):
        if not self.inicializado:
            logging.error(f"Não é possível iniciar conversa para {user_id}. IA não inicializada.")
            return None
        
        # Sua lógica de iniciar ou retomar conversa aqui
        # Exemplo:
        if user_id not in self.conversas:
             self.conversas[user_id] = self.client.chats.create(
                 model=MODEL_NAME
             )
        return self.conversas[user_id]


    def chat(self, user_id, mensagem):
        if not self.inicializado:
            logging.error("Placeholder assistente chamado, IA inoperante.")
            # Retorna a mensagem de erro que aparece no chat
            return {
                "resposta": "IA Inoperante devido a um erro de inicialização. Por favor, contate o administrador.",
                "links": {}
            }
        
        # 1. Inicia ou retoma a conversa
        conversa = self.iniciar_nova_conversa(user_id)
        if not conversa:
             return {
                "resposta": "Não foi possível iniciar a conversa. Serviço indisponível.",
                "links": {}
            }

        # 2. Envio da mensagem
        try:
            # Envia a mensagem e obtém a resposta do modelo
            response = conversa.send_message(mensagem)

            # 3. Processamento da resposta e links (Seu código anterior deve fazer isso)
            resposta_texto = response.text 
            
            # --- Exemplo de Processamento de Links (se for relevante para você) ---
            links_encontrados = self._extrair_links_e_formatar(resposta_texto)
            # ---------------------------------------------------------------------

            logging.info(f"USUÁRIO: {user_id} | IA: {resposta_texto}")

            return {
                "resposta": resposta_texto,
                "links": links_encontrados
            }

        except APIError as e:
            logging.error(f"APIError ao chamar Gemini: {e}")
            return {
                "resposta": f"Desculpe, a comunicação com a IA falhou. Erro da API: {e}",
                "links": {}
            }
        except Exception as e:
            logging.error(f"Erro inesperado no chat: {e}")
            return {
                "resposta": "Ocorreu um erro inesperado durante o processamento da sua mensagem.",
                "links": {}
            }

    # Você precisa manter este método auxiliar se estiver usando a lógica de chips de link
    def _extrair_links_e_formatar(self, texto):
        """ Extrai links do texto (exemplo) e os formata em JSON. """
        # Adapte esta lógica para o seu projeto!
        return {} # Retorna JSON vazio por simplicidade, substitua pelo seu código real.


# --- FIM DA CLASSE ASSISTENTE ---