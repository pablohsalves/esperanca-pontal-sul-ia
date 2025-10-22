# assistente_avancada.py - ARQUIVO DA LÓGICA DA IA (V9.2 - Debug de Inicialização)

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
        
        self.contatos = contatos
        self.knowledge_path = knowledge_path
        
        # 1. TENTATIVA SEGURA DE INICIALIZAÇÃO DA API
        try:
            # O cliente será inicializado mesmo que a chave esteja em um .env
            self.client = genai.Client() 
            self.model = 'gemini-2.5-flash'
        except Exception as e:
            # Se a chave da API for o problema, levante um erro informativo
            raise ValueError(f"Falha ao inicializar o cliente Gemini. Verifique a GEMINI_API_KEY: {e}")

        # 2. Leitura Segura dos Arquivos
        self.conhecimento_texto = self._ler_conhecimento()
        
        # 3. Configuração do System Instruction
        self.system_instruction = self._montar_instrucao_sistema()

    def _ler_conhecimento(self):
        """Lê o arquivo de conhecimento da igreja."""
        # Caminho absoluto para garantir que funciona no Render
        caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.knowledge_path)
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Se o Render não conseguir encontrar o arquivo, a IA irá falhar
            raise FileNotFoundError(f"Erro CRÍTICO: O arquivo de conhecimento '{self.knowledge_path}' não foi encontrado no caminho esperado: {caminho_completo}")
        except Exception as e:
            raise Exception(f"Erro na leitura do arquivo de conhecimento: {e}")


    def _montar_instrucao_sistema(self):
        """Monta a instrução de sistema que guia o comportamento da IA."""
        
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        instrucao = f"""
        # ... (O restante da sua instrução de sistema é o mesmo)
        """
        # ... (O restante da sua instrução de sistema é o mesmo)
        
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
        # ... (Mantenha o código)
        system_message = types.Content(
            role="system",
            parts=[types.Part.from_text(self.system_instruction)]
        )
        return [json.loads(system_message.model_dump_json())]

    def enviar_saudacao(self):
        # ... (Mantenha o código)
        return """
        Olá! Eu sou a **Esperança**, sua parceira de fé da Igreja da Paz Pontal Sul.
        Estou aqui para responder suas dúvidas sobre horários, localização, contatos e tudo mais sobre a nossa comunidade.
        Em que posso te ajudar hoje?
        """

    def obter_resposta_com_memoria(self, historico_serializado, nova_pergunta):
        # ... (Mantenha o código)
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
            raise Exception(f"Erro na API Google Gemini: {e.args[0]}")
        except Exception as e:
            raise Exception(f"Erro inesperado no assistente: {e}")