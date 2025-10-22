# assistente_avancada.py

import os
import random
import time 
from dotenv import load_dotenv 

from google import genai
from google.genai.errors import APIError

# Importamos a lógica de dados bíblicos local
from dados_biblicos import carregar_versiculos, versiculo_aleatorio


# --- CARREGAMENTO DE CONHECIMENTO E CHAVE API ---
load_dotenv() 
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') 

def carregar_conhecimento_igreja(caminho_arquivo: str = 'conhecimento_esperancapontalsul.txt') -> str:
    """
    Carrega o conteúdo completo do arquivo de conhecimento da igreja.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"AVISO: Arquivo de conhecimento '{caminho_arquivo}' não encontrado. A assistente não terá informações da igreja.")
        return "" 
    except Exception as e:
        print(f"ERRO ao ler o arquivo de conhecimento: {e}")
        return ""

# Instância Global do Cliente Gemini
try:
    if not GEMINI_API_KEY:
        raise ValueError("Chave API não configurada.")
    GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
except ValueError as e:
    print(f"ERRO DE INICIALIZAÇÃO DO GEMINI: {e}")
    GEMINI_CLIENT = None
    
# Definição das instruções do sistema (SYSTEM INSTRUCTION)
INSTRUCAO_SISTEMA = (
    "Você é 'Esperança', a assistente virtual da Igreja Esperança Pontal Sul. "
    "SUA ÚNICA FONTE DE INFORMAÇÃO SOBRE A IGREJA SÃO AS DIRETRIZES ABAIXO E O BANCO DE CONHECIMENTO ANEXADO À PERGUNTA. Nunca busque na internet por dados da igreja."
    "Suas respostas devem ser sempre positivas, didáticas, e baseadas em princípios bíblicos. "
    "Se a informação for sobre a igreja, use APENAS o 'BANCO DE CONHECIMENTO' fornecido. Se a resposta sobre um assunto de fé não estiver lá, use seu conhecimento bíblico, mas evite buscar na web."
)


class ParceiroDeFeAvancado:
    """
    Assistente de Atendimento que gerencia o histórico de conversação via lista de mensagens e usa Grounding.
    """
    
    def __init__(self):
        """Inicializa a assistente, carrega versículos e o conhecimento da igreja."""
        
        if GEMINI_CLIENT is None:
            raise ValueError("Cliente Gemini não pôde ser inicializado. Verifique a chave API.")
            
        self.cliente = GEMINI_CLIENT
        self.modelo = 'gemini-2.5-flash' 
        self.versiculos = carregar_versiculos()
        # Carrega o Banco de Conhecimento
        self.conhecimento_igreja = carregar_conhecimento_igreja() 
        
        print(f"Assistente Avançada inicializada com o modelo {self.modelo} e {len(self.versiculos)} versículos carregados.")

    def iniciar_novo_chat(self) -> list:
        """
        Retorna uma lista vazia, que é o formato inicial do histórico na sessão do Flask.
        """
        return []

    def _criar_chat_temporario(self, historico_mensagens: list):
        """
        Cria o objeto Chat do Gemini com base no histórico de mensagens (lista) fornecido.
        """
        return self.cliente.chats.create(
            model=self.modelo,
            history=historico_mensagens,  # O histórico salvo é passado aqui (como lista de dicionários)
            config={'system_instruction': INSTRUCAO_SISTEMA}
        )
        
    def obter_resposta_com_memoria(self, historico_mensagens: list, pergunta: str) -> tuple[str, list]:
        """
        Gera a resposta usando o histórico salvo na sessão, anexando o Banco de Conhecimento.
        """
        
        pergunta_limpa = pergunta.lower().strip()
        
        # --- 1. Lógica para Versículo Bíblico (Prioritária) ---
        if "versiculo" in pergunta_limpa or "bíblia" in pergunta_limpa or "palavra de deus" in pergunta_limpa:
            vers = versiculo_aleatorio(self.versiculos)
            return f"Claro! O Espírito Santo inspirou uma Palavra para o seu coração:\n\n{vers}", historico_mensagens
        
        # --- 2. Preparação da Pergunta com Grounding ---
        pergunta_formatada = (
            f"[INÍCIO DO BANCO DE CONHECIMENTO DA IGREJA]\n"
            f"{self.conhecimento_igreja}\n"
            f"[FIM DO BANCO DE CONHECIMENTO DA IGREJA]\n\n"
            f"Pergunta do Usuário: {pergunta}"
        )
        
        # --- 3. Geração de Resposta com Gemini (Com Lógica de Tentativa) ---
        
        max_tentativas = 3
        
        for tentativa in range(max_tentativas):
            try:
                chat_objeto = self._criar_chat_temporario(historico_mensagens)
                
                # Usa a pergunta formatada!
                response = chat_objeto.send_message(pergunta_formatada) 
                
                # Retorna a resposta E o histórico ATUALIZADO (lista de objetos Content)
                return response.text, chat_objeto.get_history()
                
            except APIError as e: 
                
                if tentativa == max_tentativas - 1:
                    print(f"\n[ERRO DE IA] Falha após {max_tentativas} tentativas. Erro: {e.status_code}")
                    return "Desculpe, o servidor da minha inteligência está muito ocupado agora. Por favor, tente fazer a pergunta novamente em instantes.", historico_mensagens
                
                tempo_espera = 2 ** tentativa 
                print(f"\n[AVISO DE IA] Tentativa {tentativa + 1} falhou. Aguardando {tempo_espera}s...")
                time.sleep(tempo_espera) 
                
            except Exception as e:
                return f"Ocorreu um erro inesperado na assistente. Por favor, tente novamente: {e}", historico_mensagens

    def enviar_saudacao(self):
        """Retorna uma saudação inicial."""
        return "Olá! Que a paz de Cristo esteja contigo. Eu sou a Esperança, sua assistente virtual da Igreja Esperança Pontal Sul. Em que posso te guiar hoje?"