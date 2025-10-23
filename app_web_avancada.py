# app_web_avancada.py - VERSÃO V60.29 (Correções Finais de API e Histórico de Sessão)

import os
import json
from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types

# --- Configuração de Links de Contato ---
CONTACT_LINKS = {
    # ... (Seus links permanecem os mesmos)
    "whatsapp": {
        "text": "Falar com a Equipe",
        "url": "https://wa.me/5562999999999?text=Ol%C3%A1%2C%20gostaria%20de%20informa%C3%A7%C3%B5es%20sobre%20a%20Hope.",
        "icon": "fab fa-whatsapp" 
    },
    "instagram": {
        "text": "Ver nosso Instagram",
        "url": "https://www.instagram.com/seuperfil",
        "icon": "fab fa-instagram"
    },
    "localizacao": {
        "text": "Ver Localização no Mapa",
        "url": "https://maps.app.goo.gl/SuaLocalizacao",
        "icon": "fas fa-map-marker-alt"
    },
    "secretaria": {
        "text": "Ir para o Portal da Secretaria",
        "url": "http://portal.suasecretaria.com.br",
        "icon": "fas fas fa-laptop"
    }
}
# --- Fim Configuração de Links ---

if 'GEMINI_API_KEY' not in os.environ:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não está configurada.")

client = genai.Client()
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura') 

KNOWLEDGE_FILE = 'conhecimento_esperancapontalsul.txt'

def load_knowledge_base():
    # ... (Função load_knowledge_base permanece a mesma)
    try:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"AVISO: Arquivo de conhecimento '{KNOWLEDGE_FILE}' não encontrado.")
        return ""
    except Exception as e:
        print(f"Erro ao ler o arquivo de conhecimento: {e}")
        return ""

KNOWLEDGE_CONTENT = load_knowledge_base()
MODEL = 'gemini-2.5-flash'
BASE_SYSTEM_INSTRUCTION = (
    "Você é HOPE, um assistente virtual amigável, prestativo e espiritual. Responda de forma concisa e útil, "
    "mantendo um tom de fé e esperança. Nunca mencione que é um modelo de linguagem ou que foi criado pelo Google. "
    "Use Markdown para formatar suas respostas, como negrito e listas. Mantenha as respostas curtas."
)

FULL_SYSTEM_INSTRUCTION = (
    BASE_SYSTEM_INSTRUCTION + 
    "\n\n--- INFORMAÇÕES ADICIONAIS DE CONTEXTO ---\n" +
    "USE ESTAS INFORMAÇÕES PRIMARIAMENTE para responder perguntas específicas da igreja (horários, eventos, etc.):\n" + 
    KNOWLEDGE_CONTENT
)

INTENT_MODEL = 'gemini-2.5-flash'
INTENT_SYSTEM_INSTRUCTION = "Você é um classificador de intenções. Sua única tarefa é identificar se a mensagem do usuário pede por 'whatsapp', 'instagram', 'localizacao' (que inclui endereço e mapa), ou 'secretaria'. Se a intenção for clara, responda APENAS com a palavra-chave (ex: 'whatsapp'). Caso contrário, responda APENAS com a palavra-chave 'chat'. Sua resposta deve ser sempre uma única palavra minúscula."

def get_gemini_response(history, user_message, system_instruction=FULL_SYSTEM_INSTRUCTION):
    """
    Função principal para obter a resposta da IA.
    """
    try:
        # A sintaxe de Part(text=...) para a mensagem do usuário está correta
        history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=config,
        )
        
        # CORREÇÃO CRÍTICA #1: Usa a sintaxe correta para adicionar a resposta da IA ao histórico.
        # Evita o erro "Part.from_text() recebe 1 argumento posicional, mas 2 foram fornecidos"
        history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
        
        return response.text
    
    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {e}")
        return "Desculpe, estou com dificuldades técnicas no momento. Tente novamente mais tarde."

def classify_intent(user_message):
    """
    Classifica a intenção do usuário para verificar se é um pedido de contato.
    """
    history = [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]
    
    config = types.GenerateContentConfig(
        system_instruction=INTENT_SYSTEM_INSTRUCTION
    )
    
    try:
        response = client.models.generate_content(
            model=INTENT_MODEL,
            contents=history,
            config=config,
        )
        return response.text.strip().lower()
        
    except Exception as e:
        print(f"Erro ao classificar a intenção: {e}")
        return "chat"

@app.route("/")
def home():
    # ... (Rota home permanece a mesma)
    if 'chat_history' not in session or not isinstance(session['chat_history'], list):
        session['chat_history'] = []
        
    saudacao = "Olá! Eu sou **HOPE**, sua parceira de fé. Como posso te ajudar hoje?"

    return render_template("chat_interface.html", saudacao=saudacao)

@app.route("/api/chat", methods=["POST"])
def chat_api():
    """
    Endpoint para comunicação AJAX com o front-end.
    """
    data = request.json
    user_message = data.get("mensagem")
    
    if not user_message:
        return jsonify({"resposta": "Por favor, envie uma mensagem."})

    intent = classify_intent(user_message)
    
    if intent in CONTACT_LINKS:
        link_info = CONTACT_LINKS[intent]
        
        response_data = {
            "type": "button",
            "pre_text": f"Claro! Aqui está o acesso para o setor de {intent.capitalize()}:",
            "button_text": link_info["text"],
            "button_url": link_info["url"],
            "button_icon": link_info["icon"]
        }
        return jsonify(response_data)
        
    else:
        history_dicts = session.get('chat_history', [])
        
        # Converte a lista de dicionários para objetos types.Content para a API
        history = []
        try:
            history = [types.Content(**h) for h in history_dicts]
        except Exception as e:
            # Caso a sessão esteja corrompida, limpa e inicia novo chat.
            print(f"Erro ao carregar histórico da sessão: {e}. Reiniciando histórico.")
            session['chat_history'] = []
            history = []

        ia_response_text = get_gemini_response(history, user_message)
        
        # CORREÇÃO CRÍTICA #2: Substitui h.to_dict() por h.model_dump() ou h.to_json()
        # O Pydantic (usado pela Google GenAI SDK) renomeou to_dict() para model_dump()
        session['chat_history'] = [h.model_dump() for h in history]
        
        return jsonify({"type": "text", "resposta": ia_response_text})

if __name__ == "__main__":
    if 'FLASK_SECRET_KEY' not in os.environ:
         os.environ['FLASK_SECRET_KEY'] = 'uma_chave_segura_para_desenvolvimento'
         
    app.run(debug=True)