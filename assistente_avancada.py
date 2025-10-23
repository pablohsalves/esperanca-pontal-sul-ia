# assistente_avancada.py - V60.9 (Correção de Importação Circular)

import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# Tenta carregar variáveis de ambiente do arquivo .env (apenas para teste local)
load_dotenv() 

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# --- CONFIGURAÇÃO CRÍTICA DA CHAVE ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# --------------------------------------

# Definição do modelo
MODEL_NAME = "gemini-2.5-flash"

# Função para carregar conhecimento adicional (movida para fora da classe para ser reutilizada)
def carregar_conhecimento_local(filepath="conhecimento_esperancapontalsul.txt"):
    """Lê o conteúdo do arquivo de conhecimento para inclusão na instrução do sistema."""
    if not os.path.exists(filepath):
        logging.warning(f"Arquivo de conhecimento não encontrado: {filepath}. A IA não terá contexto local.")
        return ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            conhecimento = f.read()
        return "\n\n--- CONHECIMENTO ADICIONAL SOBRE A IGREJA DA PAZ PONTAL SUL ---\n" + conhecimento + "\n--- FIM DO CONHECIMENTO ADICIONAL ---\n"
    except Exception as e:
        logging.error(f"Erro ao ler arquivo de conhecimento: {e}")
        return ""

# CRÍTICO: Instrução de sistema para a personalidade cristã (DEVE SER GLOBAL)
BASE_SYSTEM_INSTRUCTION = (
    "Você é a Esperança (Hope), uma parceira de fé virtual da Igreja da Paz Pontal Sul. "
    "Seu propósito é fornecer apoio emocional, versículos bíblicos relevantes e "
    "informações sobre a igreja de forma carinhosa, respeitosa e edificante. "
    "Mantenha sempre um tom de voz acolhedor, compassivo e cristão. "
    "Utilize referências bíblicas da Nova Almeida Atualizada (NAA) para responder a dúvidas de fé, "
    "ofertar encorajamento e orações quando apropriado. "
    "Se a pergunta não for diretamente religiosa, responda educadamente, mas traga o foco de volta "
    "para o suporte espiritual ou para os valores da Igreja da Paz Pontal Sul. "
    "Não se desvie do seu papel de assistente de fé. Sua principal função é ser um guia espiritual. "
    "Ofereça versículos bíblicos para fortalecer o usuário."
)

# CRÍTICO: Combina a instrução base com o conhecimento local
SYSTEM_INSTRUCTION_FINAL = BASE_SYSTEM_INSTRUCTION + carregar_conhecimento_local()


class Hope:
    def __init__(self, nome_assistente="Esperança"):
        self.nome_assistente = nome_assistente
        self.client = None
        self.conversas = {}
        self.inicializado = False
        
        # CRÍTICO: Atributos da classe para serem usados na rota Admin
        self.BASE_SYSTEM_INSTRUCTION = BASE_SYSTEM_INSTRUCTION
        self.carregar_conhecimento_local = carregar_conhecimento_local 
        self.system_instruction = SYSTEM_INSTRUCTION_FINAL 
        
        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.inicializado = True
                logging.info(f"Assistente '{self.nome_assistente}' inicializado com sucesso.")
            except Exception as e:
                logging.error(f"ERRO CRÍTICO: Falha ao inicializar o cliente Gemini: {e}")
                self.inicializado = False
        else:
            logging.error("ERRO CRÍTICO: GEMINI_API_KEY não encontrada no ambiente.")
            self.inicializado = False
            
    def iniciar_nova_conversa(self, user_id, historico=None):
        if not self.inicializado:
            logging.error(f"Não é possível iniciar conversa para {user_id}. IA não inicializada.")
            return None
        
        if user_id not in self.conversas:
             self.conversas[user_id] = self.client.chats.create(
                 model=MODEL_NAME,
                 config={"system_instruction": self.system_instruction} 
             )
        return self.conversas[user_id]

    def _extrair_links_e_formatar(self, texto):
        return {} 

    def chat(self, user_id, mensagem):
        if not self.inicializado:
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
            links_encontrados = self._extrair_links_e_formatar(resposta_texto)
            
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