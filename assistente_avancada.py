# assistente_avancada.py

from google import genai
from google.genai import types
import os
import json

class ParceiroDeFeAvancado:
    def __init__(self, modelo='gemini-2.5-flash', arquivo_conhecimento='conhecimento_esperancapontalsul.txt'):
        self.modelo = modelo
        self.client = self._iniciar_cliente()
        self.conhecimento_texto = self._carregar_conhecimento(arquivo_conhecimento)
        
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
            print(f"AVISO: Arquivo de conhecimento '{caminho}' não encontrado.")
            return """
# conhecimento_esperancapontalsul.txt

Pastor Líder: Pastor Daniel Rodrigues
Localização da Sede: Rua A-4, Quadra 44, Lote 17, Setor Garavelo, Aparecida de Goiânia - GO.
Horário de Cultos: Domingos às 19:00h e Terças-feiras (Culto da Vitória) às 19:30h.
Missão da Igreja: Levar a mensagem de Jesus Cristo a todas as famílias e formar discípulos que impactem sua comunidade com amor e esperança.
Visão Principal: Uma comunidade vibrante, centrada na Palavra de Deus (a Bíblia Sagrada), focada em missões urbanas e no discipulado.
Base Doutrinária: Ênfase na Bíblia Sagrada como a única regra de fé e prática, o Batismo nas águas por imersão, a Santa Ceia e o Poder do Espírito Santo.
Livro de Referência: A Bíblia Sagrada é o principal livro de estudo e ensino.
"""
        
    def _criar_configuracao_gemini(self):
        """Cria as configurações de sistema e safety_settings."""
        
        # 1. Instrução de Sistema (Persona e Grounding) - ATUALIZADA
        instrucao_sistema = (
            "Você é a Esperança, uma assistente virtual e parceira de fé da Igreja Esperança Pontal Sul."
            "Seu principal objetivo é fornecer respostas que refletem os ensinamentos cristãos e a doutrina da igreja."
            "Use o contexto fornecido sobre a igreja para responder a perguntas específicas sobre a Igreja Esperança Pontal Sul."
            "Mantenha um tom acolhedor, inspirador e respeitoso. Seja concisa, mas completa."
            
            "**FORMATO DE RESPOSTA:** Sempre que citar links (endereço, WhatsApp, Instagram, etc.), você DEVE usar a formatação HTML '<a>' para torná-los clicáveis."
            "Exemplos de Formatação HTML que você deve usar:"
            "1. Endereço/Google Maps: <a href=\"https://maps.app.goo.gl/seuendereco\" target=\"_blank\">Rua A-4, Q. 44, Lt. 17</a>"
            "2. WhatsApp: <a href=\"https://wa.me/5562900000000\" target=\"_blank\">Entre em Contato pelo WhatsApp</a>"
            "3. Instagram: <a href=\"https://instagram.com/seu_perfil\" target=\"_blank\">Instagram da Igreja</a>"
            "Mantenha a tag '<strong>' para ênfase (como no nome da Igreja)."
            
            "Sempre que possível, use trechos da Bíblia ou do conhecimento fornecido para dar suporte às suas respostas."
            "Se a pergunta for de natureza complexa ou pessoal, incentive o usuário a buscar a liderança ou pastores."
            
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
        try:
            resposta = chat_session.send_message(pergunta)
            
            # 4. Retornar a Resposta e o Histórico Atualizado
            return resposta.text, chat_session.get_history()
        
        except Exception as e:
            print(f"Erro ao obter resposta do Gemini: {e}")
            erro_msg = ("Desculpe, houve um erro ao processar sua solicitação no servidor de IA. "
                        "Por favor, tente novamente mais tarde.")
            
            return erro_msg, historico_objetos