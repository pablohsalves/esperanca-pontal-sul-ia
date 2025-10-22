# 🕊️ Hope - Assistente Virtual da Igreja Esperança Pontal Sul

Bem-vindo ao repositório do Hope, a assistente virtual e parceira de fé baseada em Gemini (Google) e Flask.

## 🚀 Estrutura do Projeto

* **`app_web_avancada.py`**: O arquivo principal da aplicação Flask.
    * Gerencia as rotas, autenticação de admin, logs e a comunicação com a API Gemini.
* **`assistente_avancada.py`**: A lógica do modelo de IA.
    * Define a `System Instruction` (Persona, Contexto e Formato de Chips).
* **`conhecimento_esperancapontalsul.txt`**: Base de conhecimento da IA.
    * Editável via Painel Admin (protegido por login).
* **`contatos_igreja.json`**: Mapeamento de links externos (WhatsApp, Localização, etc.).
    * Usado para gerar chips clicáveis no chat e as instruções da IA.
* **`requirements.txt`**: Lista de dependências do Python.
* **`templates/`**: Arquivos HTML (interface de chat, admin e login).
* **`static/`**: Arquivos CSS e JavaScript.

## 🔑 Configuração de Ambiente (Variáveis)

As seguintes variáveis de ambiente são **obrigatórias** para rodar a aplicação:

| Variável | Descrição |
| :--- | :--- |
| `GEMINI_API_KEY` | Chave de API para o Google Gemini. |
| `FLASK_SECRET_KEY` | Chave secreta do Flask para segurança de sessão. |
| `ADMIN_USERNAME` | Nome de usuário para o Painel Admin. |
| **`ADMIN_PASSWORD_HASH`** | **HASH bcrypt da senha do Admin.** *Não use a senha simples.* |

### Como Gerar o HASH da Senha:

Use este código Python (instale `bcrypt` primeiro com `pip install bcrypt`):

```python
import bcrypt
senha = "SUA_SENHA_SECRETA_AQUI".encode('utf-8')
print(bcrypt.hashpw(senha, bcrypt.gensalt()).decode('utf-8'))