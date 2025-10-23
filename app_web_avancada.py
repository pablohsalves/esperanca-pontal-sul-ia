# app_web_avancada.py - VERSÃO V60.20 (Completo: Botões, RAG, Correção de Sessão)

import os
import json
from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types

# --- Configuração de Links de Contato (AJUSTE AQUI) ---
# **IMPORTANTE:** Atualize os URLs com os links reais da sua instituição.
CONTACT_LINKS = {
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
        "icon": "fas fa-laptop"
    }
}
# --- Fim Configuração de Links ---

# Verifica e configura a chave Gemini
if 'GEMINI_API_KEY' not in os.environ:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não está configurada.")

# Inicialização do cliente Gemini
client = genai.Client()

# Inicialização do aplicativo Flask
app = Flask(__name__)
# Chave secreta para gerenciar sessões
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura') 

# Nome do arquivo de conhecimento
KNOWLEDGE_FILE = 'conhecimento_esperancapontalsul.txt'

def load_knowledge_base():
    """Carrega o conteúdo do arquivo de conhecimento específico (RAG)."""
    try:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"AVISO: Arquivo de conhecimento '{KNOWLEDGE_FILE}' não encontrado.")
        return ""
    except Exception as e:
        print(f"Erro ao ler o arquivo de conhecimento: {e}")
        return ""

# Carrega o conhecimento UMA VEZ ao iniciar o aplicativo
KNOWLEDGE_CONTENT = load_knowledge_base()

# Modelo e Instrução Base da IA
MODEL = 'gemini-2.5-flash'
BASE_SYSTEM_INSTRUCTION = (
    "Você é HOPE, um assistente virtual amigável, prestativo e espiritual. Responda de forma concisa e útil, "
    "mantendo um tom de fé e esperança. Nunca mencione que é um modelo de linguagem ou que foi criado pelo Google. "
    "Use Markdown para formatar suas respostas, como negrito e listas. Mantenha as respostas curtas."
)

# Combina a instrução base com o conteúdo do arquivo
FULL_SYSTEM_INSTRUCTION = (
    BASE_SYSTEM_INSTRUCTION + 
    "\n\n--- INFORMAÇÕES ADICIONAIS DE CONTEXTO ---\n" +
    "USE ESTAS INFORMAÇÕES PRIMARIAMENTE para responder perguntas específicas da igreja (horários, eventos, etc.):\n" + 
    KNOWLEDGE_CONTENT
)

# Configuração da IA para análise de intenção (para detectar botões)
INTENT_MODEL = 'gemini-2.5-flash'
INTENT_SYSTEM_INSTRUCTION = "Você é um classificador de intenções. Sua única tarefa é identificar se a mensagem do usuário pede por 'whatsapp', 'instagram', 'localizacao' (que inclui endereço e mapa), ou 'secretaria'. Se a intenção for clara, responda APENAS com a palavra-chave (ex: 'whatsapp'). Caso contrário, responda APENAS com a palavra-chave 'chat'. Sua resposta deve ser sempre uma única palavra minúscula."

def get_gemini_response(history, user_message, system_instruction=FULL_SYSTEM_INSTRUCTION):
    """
    Função principal para obter a resposta da IA.
    """
    try:
        # Adiciona a mensagem do usuário ao histórico ANTES de enviar para a API
        history.append(types.Content(role="user", parts=[types.Part.from_text(user_message)]))

        # Configurações do modelo
        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )

        # Chama a API
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=config,
        )
        
        # Adiciona a resposta da IA ao histórico para o próximo turno
        history.append(types.Content(role="model", parts=[types.Part.from_text(response.text)]))
        
        return response.text
    
    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {e}")
        return "Desculpe, estou com dificuldades técnicas no momento. Tente novamente mais tarde."

def classify_intent(user_message):
    """
    Classifica a intenção do usuário para verificar se é um pedido de contato.
    """
    history = [
        types.Content(role="user", parts=[types.Part.from_text(user_message)])
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
        # Limpa e retorna a intenção
        return response.text.strip().lower()
        
    except Exception as e:
        print(f"Erro ao classificar a intenção: {e}")
        return "chat" # Retorna chat em caso de erro

@app.route("/")
def home():
    """
    Rota inicial que exibe o chat e inicializa a sessão.
    """
    # Garante que o histórico de chat na sessão seja uma lista
    if 'chat_history' not in session or not isinstance(session['chat_history'], list):
        session['chat_history'] = []
        
    # Mensagem de saudação inicial da IA
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

    # 1. Tenta classificar a intenção do usuário
    intent = classify_intent(user_message)
    
    # 2. Verifica se a intenção é um link de contato (BOTÃO CLICÁVEL)
    if intent in CONTACT_LINKS:
        link_info = CONTACT_LINKS[intent]
        
        # Cria a resposta estruturada para o Front-end
        response_data = {
            "type": "button",
            "pre_text": f"Claro! Aqui está o acesso para o setor de {intent.capitalize()}:",
            "button_text": link_info["text"],
            "button_url": link_info["url"],
            "button_icon": link_info["icon"]
        }
        
        # Retorna o dicionário serializado
        return jsonify(response_data)
        
    # 3. Se não for link de contato, usa a IA para responder normalmente
    else:
        # Recupera o histórico da sessão
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

        # Obtém a resposta da IA (com o contexto do arquivo embutido)
        ia_response_text = get_gemini_response(history, user_message)
        
        # Atualiza o histórico de chat na sessão
        session['chat_history'] = [h.to_dict() for h in history]
        
        # Retorna a resposta da IA no formato padrão (string)
        return jsonify({"type": "text", "resposta": ia_response_text})

if __name__ == "__main__":
    # Garante que a chave secreta seja definida ao rodar localmente
    if 'FLASK_SECRET_KEY' not in os.environ:
         os.environ['FLASK_SECRET_KEY'] = 'uma_chave_segura_para_desenvolvimento'
         
    app.run(debug=True)