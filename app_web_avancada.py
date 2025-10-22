# app_web_avancada.py - ARQUIVO PRINCIPAL DO FLASK (v3.0)

from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import json
import os
import logging
import bcrypt # Novo: Para autenticação
from functools import wraps # Novo: Para criar o decorador de login
from assistente_avancada import ParceiroDeFeAvancado
from dotenv import load_dotenv

# --- Carregamento de Variáveis de Ambiente ---
load_dotenv() 

# --- CONFIGURAÇÃO DE SEGURANÇA E AMBIENTE ---
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave_padrao_muito_segura_troque_isso') 

# Credenciais de Admin carregadas do ambiente
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

# --- CONFIGURAÇÃO DE LOGS ---
# Cria um logger que salva em 'conversas.log'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    handlers=[
                        logging.FileHandler("conversas.log", encoding='utf-8'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÃO DE ARQUIVOS DE DADOS ---
CONHECIMENTO_PATH = 'conhecimento_esperancapontalsul.txt'
CONTATOS_PATH = 'contatos_igreja.json'


# --- 1. FUNÇÕES DE ADMIN E DADOS ---

def admin_required(f):
    """Decorador para proteger rotas de administração."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in') != True:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def ler_conhecimento_atual():
    """Lê o conteúdo atual do arquivo de conhecimento."""
    caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONHECIMENTO_PATH)
    try:
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "# Arquivo de conhecimento não encontrado. Conteúdo padrão de fallback."
    except Exception as e:
        return f"ERRO ao ler o arquivo: {e}"

def salvar_novo_conhecimento(novo_conteudo):
    """Sobrescreve o arquivo de conhecimento com o novo conteúdo."""
    caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONHECIMENTO_PATH)
    try:
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        return True
    except Exception as e:
        logger.error(f"ERRO ao salvar o conhecimento: {e}")
        return False
        
def carregar_links_contatos():
    """Carrega os links de contatos do JSON."""
    caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONTATOS_PATH)
    try:
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"ERRO ao carregar links de contatos: {e}")
        return {}


# --- 2. INICIALIZAÇÃO DA ASSISTENTE ---

try:
    # Passamos os links e contatos para a assistente
    assistente = ParceiroDeFeAvancado(contatos=carregar_links_contatos())
except ValueError as e:
    logger.critical(f"ERRO CRÍTICO: Falha ao inicializar o ParceiroDeFeAvancado. {e}")


# ----------------------------------------------------
# 3. ROTAS DO FLASK
# ----------------------------------------------------

# --- Rotas de Autenticação ---

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == ADMIN_USERNAME and 
            bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH.encode('utf-8'))):
            
            session['logged_in'] = True
            next_url = request.args.get('next') or url_for('admin_conhecimento')
            return redirect(next_url)
        else:
            return render_template('login.html', mensagem="Nome de usuário ou senha incorretos.")
            
    return render_template('login.html')

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


# --- Rota Principal (Chat) ---

@app.route('/')
def index():
    if 'historico' not in session:
        session['historico'] = assistente.iniciar_novo_chat()
    
    # Carrega os links para os chips dinâmicos
    links = carregar_links_contatos()
    
    saudacao_html = assistente.enviar_saudacao()
    return render_template('chat_interface.html', saudacao=saudacao_html, links=links)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pergunta = data.get('pergunta')
    historico_serializado = session.get('historico', [])
    
    if not pergunta:
        return jsonify({'erro': 'Pergunta vazia.'}), 400

    # 1. Adiciona a pergunta do usuário ao histórico (para logs e contexto)
    historico_serializado.append({
        "role": "user",
        "parts": [{"text": pergunta}]
    })

    resposta_ia = "Desculpe, a IA está indisponível no momento. Tente novamente mais tarde."
    
    try:
        # 2. Obtém a resposta e o histórico atualizado
        resposta_ia, novo_historico_gemini = assistente.obter_resposta_com_memoria(
            historico_serializado, 
            pergunta
        )
        
        # 3. Atualiza o histórico na sessão
        novo_historico_serializado = [
            json.loads(item.model_dump_json()) 
            for item in novo_historico_gemini
        ]
        session['historico'] = novo_historico_serializado
        
    except Exception as e:
        # 4. Tratamento de Erros: Loga o erro e usa a mensagem padrão
        logger.error(f"Erro na API Gemini para a pergunta '{pergunta[:50]}...': {e}", exc_info=True)
        # Mantém a resposta padrão de erro definida acima
        pass 
    finally:
        # 5. Log de Conversa (Pergunta e Resposta)
        logger.info(f"USER: {pergunta} | IA: {resposta_ia}")
    
    return jsonify({'resposta': resposta_ia})


# --- Rota de Administração (Protegida) ---

@app.route('/admin/conhecimento', methods=['GET', 'POST'])
@admin_required
def admin_conhecimento():
    """Painel de administração para editar o arquivo de conhecimento."""
    mensagem = ""
    
    if request.method == 'POST':
        novo_conteudo = request.form['novo_conhecimento']
        
        if salvar_novo_conhecimento(novo_conteudo):
            # Recarrega a instância do assistente para forçar a leitura do novo arquivo
            assistente.conhecimento_texto = ler_conhecimento_atual()
            mensagem = "Conhecimento atualizado com sucesso! (A IA recarregou o novo texto.)"
        else:
            mensagem = "Erro ao salvar o novo conhecimento. Verifique as permissões e logs."
            
        conteudo_atual = novo_conteudo
    else:
        conteudo_atual = ler_conhecimento_atual()

    return render_template('admin_conhecimento.html', 
                           conteudo_atual=conteudo_atual, 
                           mensagem=mensagem)


if __name__ == '__main__':
    app.run(debug=True)