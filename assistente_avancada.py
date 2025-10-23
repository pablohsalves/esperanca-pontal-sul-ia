# assistente_avancada.py - PARCEIRO DE FÉ AVANÇADO (FINAL)

import os
import json
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

# O texto inicial que define o comportamento do assistente
INSTRUCAO_SISTEMA_PADRAO = """
Você é Esperança, uma parceira de fé virtual, desenvolvida para auxiliar a Igreja Esperança Pontal Sul.
Seu objetivo principal é oferecer informações sobre a igreja, seus horários, localização, 
princípios e contatos, com uma abordagem acolhedora, cristã e inspirada na Bíblia.

Sua personalidade é:
1. Acolhedora e Pastoral: Mantenha um tom de fé, esperança e amor.
2. Informativa: Baseie-se nas informações de CONHECIMENTO_ATUAL.
3. Objetiva: Responda diretamente ao que foi perguntado.
4. Use emojis cristãos e de paz (ex: 🕊️, 🙏, 💖).

INSTRUÇÕES ESPECÍFICAS:
- Nunca gere imagens.
- Não crie ou sugira rituais ou dogmas que não estejam explicitamente no CONHECIMENTO_ATUAL.
- Mantenha respostas curtas e diretas. Se a resposta for longa, use parágrafos.
- Sempre que a resposta for um link de contato ou localização (WhatsApp, Mapa, Horários),
  sugira o link usando um 'chip' de link clicável no formato HTML:
  <a href="{URL}" target="_blank" class="chip link-chip">{TEXTO}</a>
  
### CONHECIMENTO_ATUAL ###
{CONHECIMENTO_TEXTO}

### LINKS_DE_CONTATO ###
{LINKS_DE_CONTATO}

"""

class ParceiroDeFeAvancado:
    def __init__(self, contatos, conhecimento_texto=None):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("A variável de ambiente GEMINI_API_KEY não está configurada.")

        self.client = genai.Client(api_key=self.api_key)
        self.model = 'gemini-2.5-flash'  # Modelo rápido para chat
        
        # Dados de contexto
        self.contatos = contatos
        self.conhecimento_texto = conhecimento_texto if conhecimento_texto is not None else self._carregar_conhecimento_padrao()
        
        # Atualiza a instrução do sistema com o conhecimento carregado
        self._atualizar_instrucao_sistema()

    def _carregar_conhecimento_padrao(self):
        """Carrega o conhecimento do arquivo padrão."""
        try:
            with open('conhecimento_esperancapontalsul.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("Arquivo 'conhecimento_esperancapontalsul.txt' não encontrado. Usando conhecimento vazio.")
            return "Nenhum conhecimento base disponível."
            
    def _atualizar_instrucao_sistema(self):
        """Gera a instrução completa do sistema com contexto."""
        links_json = json.dumps(self.contatos, indent=2, ensure_ascii=False)
        self.instrucao_sistema = INSTRUCAO_SISTEMA_PADRAO.format(
            CONHECIMENTO_TEXTO=self.conhecimento_texto,
            LINKS_DE_CONTATO=links_json
        )

    def iniciar_novo_chat(self):
        """Inicia um novo histórico de chat."""
        # Retorna o formato serializável (lista de dicionários)
        return []

    def enviar_saudacao(self):
        """Gera a saudação inicial usando o modelo."""
        prompt = "Gere uma breve e calorosa mensagem de saudação inicial para um visitante do chat."
        
        # Cria uma sessão temporária de chat apenas para a saudação
        chat = self.client.chats.create(
            model=self.model,
            system_instruction=self.instrucao_sistema
        )
        
        try:
            response = chat.send_message(prompt)
            return response.text
        except APIError as e:
            logger.error(f"Erro na API ao gerar saudação: {e}")
            return "Olá! Sou Esperança, sua parceira de fé virtual. Tivemos um pequeno erro técnico, mas estou aqui para te ajudar. Como posso servir?"
        except Exception as e:
            logger.error(f"Erro inesperado ao gerar saudação: {e}")
            return "Olá! Sou Esperança, sua parceira de fé virtual. O servidor de IA falhou ao iniciar, mas estou aqui para te ajudar. Como posso servir?"


    def obter_resposta_com_memoria(self, historico_serializado, pergunta):
        """
        Recebe o histórico serializado (lista de dicts), reconstrói o objeto Content, 
        envia a pergunta e retorna a resposta e o novo histórico serializável.
        """
        
        # 1. Reconstruir o histórico de Content a partir do JSON serializado
        historico_gemini = []
        for item in historico_serializado:
            try:
                # CORREÇÃO CRÍTICA: Tenta reconstruir o objeto Content passando o dicionário.
                # A classe types.Content (ou types.Content) suporta o construtor direto
                historico_gemini.append(types.Content(**item))
            except Exception as e:
                # Se falhar (como o erro from_dict), retorna o erro para debug
                logger.error(f"Falha ao reconstruir item do histórico: {item}. Erro: {e}")
                raise e # Propaga o erro para que o log do render o pegue.

        # 2. Iniciar ou continuar o chat com o histórico reconstruído
        chat = self.client.chats.create(
            model=self.model,
            system_instruction=self.instrucao_sistema,
            history=historico_gemini
        )
        
        # 3. Enviar a nova mensagem
        response = chat.send_message(pergunta)
        
        # 4. Preparar o histórico para a sessão (Serialização)
        # O objeto de histórico do chat.get_history() contém os Content gerados pelo modelo.
        novo_historico_gemini = chat.get_history()
        
        return response.text, novo_historico_gemini