# app_web_avancada.py - ARQUIVO PRINCIPAL DO FLASK (v5.0 - ADMIN ABERTO E ESTÁVEL, COM ROBUSTEZ)

from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import json
import os
import logging
# Removidos: import bcrypt e from functools import wraps
from assistente_avancada import ParceiroDeFeAvancado
from dotenv import load_dotenv

# --- Carregamento de Variáveis de Ambiente ---
load_dotenv() 

# --- CONFIGURAÇÃO DE SEGURANÇA E AMBIENTE ---
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave_padrao_muito_segura_troque_isso') 

# --- CONFIGURAÇÃO DE LOGS ---
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


# --- 1. FUNÇÕES DE DADOS ---

def ler_conhecimento_atual():
    """Lê o conteúdo atual do arquivo de conhecimento."""
    caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONHECIMENTO_PATH)
    try:
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "# Arquivo de conhecimento não encontrado. Conteúdo padrão de fallback."

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
    assistente = ParceiroDeFeAvancado(contatos=carregar_links_contatos())
except Exception as e:
    logger.critical(f"ERRO CRÍTICO: Falha ao inicializar o ParceiroDeFeAvancado. {e}")
    # Cria uma classe placeholder (fallback) para evitar que o app trave
    class PlaceholderAssistente:
        def iniciar_novo_chat(self): return []
        def enviar_saudacao(self): return "<h1>ERRO CRÍTICO</h1><p>O assistente de IA não pôde ser inicializado. Verifique logs e chaves API.</p>"
        def obter_resposta_com_memoria(self, hist, perg): return "IA Inoperante devido a erro de inicialização.", hist
        def __setattr__(self, name, value):
            if name in ['contatos', 'conhecimento_texto']:
                pass # Não permite alterar propriedades no placeholder
            else:
                super().__setattr__(name, value)
        
    assistente = PlaceholderAssistente()


# ----------------------------------------------------
# 3. ROTAS DO FLASK
# ----------------------------------------------------

@app.route('/')
def index():
    # Bloco robusto para garantir a inicialização da sessão
    try:
        if 'historico' not in session:
            session['historico'] = assistente.iniciar_novo_chat() 
    except Exception as e:
        # Se a IA travar aqui (ex: falha na API key), limpa a sessão e tenta de novo.
        logger.error(f"Erro ao iniciar histórico da sessão: {e}. Limpando a sessão.")
        session.pop('historico', None) # Remove histórico corrompido
        if 'historico' not in session:
             session['historico'] = assistente.iniciar_novo_chat() 
             
    # Carrega os links e a saudação
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

    historico_serializado.append({
        "role": "user",
        "parts": [{"text": pergunta}]
    })

    resposta_ia = "Desculpe, houve um erro de comunicação com a IA. Por favor, tente novamente mais tarde."
    
    try:
        resposta_ia, novo_historico_gemini = assistente.obter_resposta_com_memoria(
            historico_serializado, 
            pergunta
        )
        
        novo_historico_serializado = [
            json.loads(item.model_dump_json()) 
            for item in novo_historico_gemini
        ]
        session['historico'] = novo_historico_serializado
        
    except Exception as e:
        logger.error(f"Erro na API Gemini para a pergunta '{pergunta[:50]}...': {e}", exc_info=True)
        resposta_ia = f"Erro Interno: {str(e)[:100]}..." 
        pass 
    finally:
        logger.info(f"USER: {pergunta} | IA: {resposta_ia}")
    
    return jsonify({'resposta': resposta_ia})


# --- Rota de Administração (PÚBLICA) ---

@app.route('/admin/conhecimento', methods=['GET', 'POST'])
def admin_conhecimento():
    mensagem = ""
    
    if request.method == 'POST':
        novo_conteudo = request.form['novo_conhecimento']
        
        # Estas linhas são seguras, pois o PlaceholderAssistente as ignora.
        assistente.contatos = carregar_links_contatos()
        
        if salvar_novo_conhecimento(novo_conteudo):
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')