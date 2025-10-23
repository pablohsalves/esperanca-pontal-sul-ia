# app_web_avancada.py - VERSÃO V60.40 (Admin /conhecimento RESTAURADO)

import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash

# Importação do Google GenAI
from google import genai
from google.genai import types

# --- Configuração de Links de Contato ---
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
        "icon": "fas fas fa-laptop"
    }
}
# --- Fim Configuração de Links ---

if 'GEMINI_API_KEY' not in os.environ:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não está configurada.")

# Configuração de Admin BÁSICA
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin') # Usuário padrão
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'suasenhafacil') # Senha padrão (MUDE ISSO)

client = genai.Client()
app = Flask(__name__)
# CRÍTICO: Garante que você tenha um FLASK_SECRET_KEY configurado para usar `flash` e `session`
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura') 

KNOWLEDGE_FILE = 'conhecimento_esperancapontalsul.txt'

def load_knowledge_base():
    """Tenta carregar o conteúdo do arquivo de conhecimento."""
    try:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            print("INFO: Arquivo de conhecimento carregado com sucesso.")
            return content
    except FileNotFoundError:
        print(f"CRÍTICO: Arquivo de conhecimento '{KNOWLEDGE_FILE}' não encontrado.")
        return ""
    except Exception as e:
        print(f"ERRO: Falha ao ler o arquivo de conhecimento: {e}")
        return ""
    
def save_knowledge_base(content):
    """Tenta salvar o conteúdo no arquivo de conhecimento."""
    try:
        with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        # Recarrega o conteúdo global após a escrita
        global KNOWLEDGE_CONTENT
        KNOWLEDGE_CONTENT = content
        print("INFO: Arquivo de conhecimento salvo e base recarregada com sucesso.")
        return True
    except Exception as e:
        print(f"ERRO: Falha ao salvar o arquivo de conhecimento: {e}")
        return False

KNOWLEDGE_CONTENT = load_knowledge_base()
MODEL = 'gemini-2.5-flash'
BASE_SYSTEM_INSTRUCTION = (
    "Você é HOPE, um assistente virtual amigável, prestativo e espiritual. Responda de forma concisa e útil, "
    "mantendo um tom de fé e esperança. Nunca mencione que é um modelo de linguagem ou que foi criado pelo Google. "
    "Use Markdown para formatar suas respostas, como negrito e listas. Mantenha as respostas curtas."
)

# Funções para IA (permanecem as mesmas)
def update_system_instruction():
    """Atualiza a instrução do sistema com o conteúdo da base de conhecimento."""
    global FULL_SYSTEM_INSTRUCTION
    if KNOWLEDGE_CONTENT:
        FULL_SYSTEM_INSTRUCTION = (
            BASE_SYSTEM_INSTRUCTION + 
            "\n\n--- INFORMAÇÕES ADICIONAIS DE CONTEXTO ---\n" +
            "USE ESTAS INFORMAÇÕES PRIMARIAMENTE para responder perguntas específicas da igreja (horários, eventos, nome do pastor, etc.):\n" + 
            KNOWLEDGE_CONTENT
        )
    else:
        FULL_SYSTEM_INSTRUCTION = BASE_SYSTEM_INSTRUCTION

update_system_instruction() # Chama para inicializar

# ... (o restante das funções get_gemini_response e classify_intent permanecem iguais) ...
def get_gemini_response(history, user_message, system_instruction=FULL_SYSTEM_INSTRUCTION):
    """
    Função principal para obter a resposta da IA.
    """
    # ... (código da função) ...
    try:
        history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=config,
        )
        
        history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
        
        return response.text
    
    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {e}")
        return "Desculpe, estou com dificuldades técnicas no momento. Por favor, tente novamente mais tarde."

def classify_intent(user_message):
    history = [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]
    
    config = types.GenerateContentConfig(
        system_instruction="Você é um classificador de intenções. Sua única tarefa é identificar se a mensagem do usuário pede por 'whatsapp', 'instagram', 'localizacao' (que inclui endereço e mapa), ou 'secretaria'. Se a intenção for clara, responda APENAS com a palavra-chave (ex: 'whatsapp'). Caso contrário, responda APENAS com a palavra-chave 'chat'. Sua resposta deve ser sempre uma única palavra minúscula."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=history,
            config=config,
        )
        return response.text.strip().lower()
        
    except Exception as e:
        print(f"Erro ao classificar a intenção: {e}")
        return "chat"


@app.route("/")
def home():
    if 'chat_history' not in session or not isinstance(session['chat_history'], list):
        session['chat_history'] = []
        
    saudacao = "Olá! Eu sou **HOPE**, sua parceira de fé. Como posso te ajudar hoje?"

    return render_template("chat_interface.html", saudacao=saudacao)

@app.route("/knowledge_status")
def knowledge_status():
    if KNOWLEDGE_CONTENT:
        return jsonify({
            "status": "OK",
            "message": "Base de conhecimento carregada com sucesso. Verifique se o conteúdo abaixo está correto. Se sim, o modelo deve conseguir responder.",
            "content_snippet": KNOWLEDGE_CONTENT[:500] + ("..." if len(KNOWLEDGE_CONTENT) > 500 else ""),
            "content_length": len(KNOWLEDGE_CONTENT)
        })
    else:
        return jsonify({
            "status": "FALHA",
            "message": "Base de conhecimento NÃO carregada. Verifique se o arquivo 'conhecimento_esperancapontalsul.txt' existe.",
            "content_length": 0
        })

# Rota para Login (Necessária para proteger /admin/conhecimento)
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash("Login realizado com sucesso!", "message")
            return redirect(url_for('admin_conhecimento'))
        else:
            flash("Credenciais inválidas. Tente novamente.", "error")
            
    return render_template("admin_login.html")


# V60.40: Rota de Admin RESTAURADA (agora protegida)
@app.route("/admin/conhecimento", methods=["GET", "POST"])
def admin_conhecimento():
    if not session.get('logged_in'):
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('admin_login'))

    if request.method == "POST":
        novo_conhecimento = request.form.get("conhecimento")
        if novo_conhecimento is not None:
            if save_knowledge_base(novo_conhecimento):
                update_system_instruction()
                flash("Conhecimento salvo e IA recarregada com sucesso!", "message")
            else:
                flash("ERRO ao salvar o arquivo no servidor. Tente novamente.", "error")
        return redirect(url_for('admin_conhecimento'))

    # GET request
    return render_template("admin_conhecimento.html", conhecimento=KNOWLEDGE_CONTENT)

# Rota de Logout (Opcional, mas recomendado)
@app.route("/admin/logout")
def admin_logout():
    session.pop('logged_in', None)
    flash("Você saiu da área administrativa.", "message")
    return redirect(url_for('home'))


@app.route("/api/chat", methods=["POST"])
def chat_api():
    # ... (código da rota API de chat permanece o mesmo) ...
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