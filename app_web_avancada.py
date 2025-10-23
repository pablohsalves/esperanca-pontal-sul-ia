# app_web_avancada.py - VERSÃO V60.34 (Correção da Base de Conhecimento e Funcionalidade)

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
    """Tenta carregar o conteúdo do arquivo de conhecimento."""
    try:
        # Usar um encoding mais robusto
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Adicionar uma verificação simples: se estiver vazio, retorna falha
            if not content.strip():
                 print("AVISO: Arquivo de conhecimento carregado, mas está vazio.")
                 return ""
            print("INFO: Arquivo de conhecimento carregado com sucesso.")
            return content
    except FileNotFoundError:
        print(f"CRÍTICO: Arquivo de conhecimento '{KNOWLEDGE_FILE}' não encontrado.")
        return ""
    except Exception as e:
        print(f"ERRO: Falha ao ler o arquivo de conhecimento: {e}")
        return ""

KNOWLEDGE_CONTENT = load_knowledge_base()
MODEL = 'gemini-2.5-flash'
BASE_SYSTEM_INSTRUCTION = (
    "Você é HOPE, um assistente virtual amigável, prestativo e espiritual. Responda de forma concisa e útil, "
    "mantendo um tom de fé e esperança. Nunca mencione que é um modelo de linguagem ou que foi criado pelo Google. "
    "Use Markdown para formatar suas respostas, como negrito e listas. Mantenha as respostas curtas."
)

# Adiciona o conteúdo do arquivo SE ele existir e não estiver vazio.
if KNOWLEDGE_CONTENT:
    FULL_SYSTEM_INSTRUCTION = (
        BASE_SYSTEM_INSTRUCTION + 
        "\n\n--- INFORMAÇÕES ADICIONAIS DE CONTEXTO ---\n" +
        "USE ESTAS INFORMAÇÕES PRIMARIAMENTE para responder perguntas específicas da igreja (horários, eventos, nome do pastor, etc.):\n" + 
        KNOWLEDGE_CONTENT
    )
else:
    FULL_SYSTEM_INSTRUCTION = BASE_SYSTEM_INSTRUCTION


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
            system_instruction=system_instruction # Garante que a instrução completa seja passada
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=config,
        )
        
        # Correção Crítica de Histórico
        history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
        
        return response.text
    
    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {e}")
        # Retorna uma mensagem amigável no caso de falha
        return "Desculpe, estou com dificuldades técnicas no momento. Por favor, tente novamente mais tarde."

def classify_intent(user_message):
    # ... (Função classify_intent permanece a mesma)
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
    # ... (chat_api permanece a mesma - usa o novo get_gemini_response)
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
        
        history = []
        try:
            history = [types.Content(**h) for h in history_dicts]
        except Exception as e:
            print(f"Erro ao carregar histórico da sessão: {e}. Reiniciando histórico.")
            session['chat_history'] = []
            history = []

        ia_response_text = get_gemini_response(history, user_message)
        
        session['chat_history'] = [h.model_dump() for h in history]
        
        return jsonify({"type": "text", "resposta": ia_response_text})

if __name__ == "__main__":
    if 'FLASK_SECRET_KEY' not in os.environ:
         os.environ['FLASK_SECRET_KEY'] = 'uma_chave_segura_para_desenvolvimento'
         
    app.run(debug=True)