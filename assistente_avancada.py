# assistente_avancada.py (v3.0 - Com Links Externos)

from google import genai
from google.genai import types
import os
import json

class ParceiroDeFeAvancado:
    # Adicionamos o parâmetro 'contatos'
    def __init__(self, modelo='gemini-2.5-flash', arquivo_conhecimento='conhecimento_esperancapontalsul.txt', contatos=None):
        self.modelo = modelo
        self.client = self._iniciar_cliente()
        self.conhecimento_texto = self._carregar_conhecimento(arquivo_conhecimento)
        self.contatos = contatos if contatos is not None else {}
        
        print(f"Assistente Avançada inicializada com o modelo {self.modelo} e {len(self.conhecimento_texto.splitlines())} linhas de conhecimento carregadas.")

    def _iniciar_cliente(self):
        """Inicializa o cliente Gemini usando a chave de ambiente."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("A variável de ambiente 'GEMINI_API_KEY' não está configurada.")
        return genai.Client(api_key=api_key)

    def _carregar_conhecimento(self, caminho):
        """Carrega o texto de conhecimento de um arquivo local."""
        try:
            caminho_absoluto = os.path.join(os.path.dirname(__file__), caminho)
            with open(caminho_absoluto, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "# Arquivo de conhecimento não encontrado. Conteúdo padrão de fallback."
        
    def _criar_configuracao_gemini(self):
        """Cria as configurações de sistema e safety_settings."""
        
        # Gera uma lista de instruções de chips baseada no contatos_igreja.json
        instrucoes_chips = []
        for chave, dados in self.contatos.items():
            instrucoes_chips.append(f" - Para '{chave}': use <span class=\"chip {dados['classe']}\" data-url=\"{dados['url']}\">{dados['texto']}</span>")
            
        chips_str = "\n".join(instrucoes_chips)
        
        # 1. Instrução de Sistema (Persona e Grounding) - ATUALIZADA PARA O NOVO FORMATO DE LINKS
        instrucao_sistema = (
            "Você é a Esperança, uma assistente virtual e parceira de fé da Igreja Esperança Pontal Sul."
            "Seu principal objetivo é fornecer respostas que refletem os ensinamentos cristãos e a doutrina da igreja."
            "Use o contexto fornecido sobre a igreja para responder a perguntas específicas sobre a Igreja Esperança Pontal Sul."
            "Mantenha um tom acolhedor, inspirador e respeitoso. Seja concisa, mas completa."
            
            "**FORMATO DE LINKS/AÇÕES:** Sempre que citar informações de contato ou localização, você DEVE usar a formatação HTML de CHIP/BOTÃO CLICÁVEL."
            "**SINTAXE DEVE SER:** <span class=\"chip [tipo]\" data-url=\"https://www.collinsdictionary.com/dictionary/spanish-english/completa\">Texto do Botão</span>"
            "Use quebras de linha (<br>) ou espaços para separar os chips do texto."
            
            f"\n**Instruções Específicas de Chips (Baseado em contatos_igreja.json):**\n{chips_str}\n"
            
            "Mantenha a tag '<strong>' para ênfase (como no nome da Igreja)."
            "Sempre que possível, use trechos da Bíblia ou do conhecimento fornecido para dar suporte às suas respostas."
            
            f"Contexto da Igreja: {self.conhecimento_texto}" 
        )
        
        # 2. Safety Settings 
        safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
        
        return types.GenerateContentConfig(
            system_instruction=instrucao_sistema,
            safety_settings=safety_settings
        )
        
    def enviar_saudacao(self):
        """Retorna a mensagem de saudação inicial."""
        return (
            "<strong>Esperança:</strong> Olá! Que alegria ter você aqui. Sou a Esperança, sua assistente virtual "
            "e parceira de fé da Igreja Esperança Pontal Sul. Como posso te ajudar hoje?"
        )
        
    # ... (Resto da classe: iniciar_novo_chat e obter_resposta_com_memoria são iguais) ...
    def iniciar_novo_chat(self):
        """Retorna o histórico inicial serializado com a saudação da IA."""
        primeira_mensagem_ia = types.Content(
            role="model",
            parts=[types.Part.from_text(text=self.enviar_saudacao())] 
        )
        
        return [json.loads(primeira_mensagem_ia.model_dump_json())]

    def obter_resposta_com_memoria(self, historico_serializado: list, pergunta: str) -> tuple[str, list]:
        """
        Recebe o histórico serializado, envia a pergunta ao Gemini e retorna
        a resposta e o novo histórico completo.
        """
        
        # 1. Deserializar o Histórico
        try:
             historico_objetos = [
                types.Content.model_validate(item) 
                for item in historico_serializado
            ]
        except Exception as e:
            print(f"AVISO: Falha ao deserializar o histórico ({e}). Iniciando novo chat.")
            historico_objetos = []
            
        # 2. Criar a sessão de chat com as configurações
        configuracao_gemini = self._criar_configuracao_gemini()
        
        chat_session = self.client.chats.create(
            model=self.modelo,
            history=historico_objetos,
            config=configuracao_gemini
        )
        
        # 3. Enviar a Pergunta
        resposta = chat_session.send_message(pergunta)
            
        # 4. Retornar a Resposta e o Histórico Atualizado
        return resposta.text, chat_session.get_history()