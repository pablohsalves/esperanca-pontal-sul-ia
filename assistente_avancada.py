# assistente_avancada.py - ARQUIVO DA LÓGICA DA IA (Corrigido para evitar ImportError)

import os
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from datetime import datetime

# CRÍTICO: Remova QUALQUER linha aqui que diga 'from assistente_avancada import ...'

class ParceiroDeFeAvancado:
    """
    Classe responsável por interagir com a API Gemini, manter o histórico 
    e contextualizar as respostas com o conhecimento da igreja.
    """
    def __init__(self, contatos, knowledge_path='conhecimento_esperancapontalsul.txt'):
        
        # 1. Configuração da API
        # Certifique-se de que a variável GEMINI_API_KEY está definida no Render
        self.client = genai.Client() 
        self.contatos = contatos
        self.knowledge_path = knowledge_path
        self.conhecimento_texto = self._ler_conhecimento()
        
        # 2. Configuração do Modelo e System Instruction
        self.model = 'gemini-2.5-flash'
        self.system_instruction = self._montar_instrucao_sistema()

    def _ler_conhecimento(self):
        """Lê o arquivo de conhecimento da igreja."""
        try:
            # Caminho absoluto para garantir que funciona no Render
            caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.knowledge_path)
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "Nenhum conhecimento base encontrado."

    def _montar_instrucao_sistema(self):
        """Monta a instrução de sistema que guia o comportamento da IA."""
        
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        instrucao = f"""
        Você é a "Esperança", a inteligência artificial Parceira de Fé da Igreja da Paz Pontal Sul.
        Seu propósito é fornecer informações úteis e acolhedoras sobre a igreja, com foco em:
        1. Acolhimento e linguagem amigável (sempre use um tom de esperança e carinho).
        2. Responder perguntas baseando-se EXCLUSIVAMENTE no CONHECIMENTO fornecido abaixo e nos CONTATOS.
        3. Se a informação não estiver no CONHECIMENTO, diga educadamente que não possui essa informação específica.
        4. O contexto da data atual é: {data_atual}.

        --- CONHECIMENTO DA IGREJA ---
        {self.conhecimento_texto}
        
        --- CONTATOS E LINKS PARA CHIPS ---
        {json.dumps(self.contatos, indent=2, ensure_ascii=False)}

        --- INSTRUÇÕES DE FORMATAÇÃO E CHIPS ---
        - Sempre use Markdown para formatar a resposta (negrito, listas, parágrafos).
        - Se a resposta incluir informações que você possa confirmar com um link dos CONTATOS (WhatsApp, Localização, Cultos, etc.),
          você DEVE incluir o chip de ação na sua resposta em um bloco HTML simples.
        - Formato do Chip:
          <div class="chip-container">
              <div class="chip [classe_do_chip]" data-url="[link_do_contato]" data-text="[Texto do Botão]">
                  [Texto do Botão]
              </div>
          </div>
        - O [link_do_contato] deve vir diretamente do JSON de CONTATOS.
        - As classes de chips disponíveis são: localizacao, whatsapp, instagram, cultos. Use a classe apropriada.
        """
        return instrucao

    def iniciar_novo_chat(self):
        """Cria e retorna o histórico inicial com a System Instruction."""
        
        system_message = types.Content(
            role="system",
            parts=[types.Part.from_text(self.system_instruction)]
        )
        return [json.loads(system_message.model_dump_json())]

    def enviar_saudacao(self):
        """Envia a mensagem de boas-vindas inicial da IA."""
        return """
        Olá! Eu sou a **Esperança**, sua parceira de fé da Igreja da Paz Pontal Sul.
        Estou aqui para responder suas dúvidas sobre horários, localização, contatos e tudo mais sobre a nossa comunidade.
        Em que posso te ajudar hoje?
        """

    def obter_resposta_com_memoria(self, historico_serializado, nova_pergunta):
        """Obtém a resposta da IA mantendo o histórico da conversa."""
        
        historico_gemini = [
            types.Content.from_dict(item) 
            for item in historico_serializado
        ]
        
        chat = self.client.chats.create(
            model=self.model,
            history=historico_gemini,
        )

        try:
            response = chat.send_message(nova_pergunta)
            novo_historico = chat.get_history()

            return response.text, novo_historico
            
        except APIError as e:
            # Propaga o erro para ser tratado no Flask
            raise Exception(f"Erro na API Google Gemini: {e.args[0]}")
        except Exception as e:
            raise Exception(f"Erro inesperado no assistente: {e}")