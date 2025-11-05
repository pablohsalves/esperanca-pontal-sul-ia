# 📄 Documentação do Projeto: Hope - Assistente Virtual de Fé

## 1. Visão Geral do Projeto

| Característica | Detalhes |
| :--- | :--- |
| **Nome** | Hope - Assistente Virtual de Fé |
| **Propósito** | Fornecer suporte interativo e informações instantâneas sobre a Igreja Evangélica Esperança Pontal Sul, utilizando Inteligência Artificial. |
| **Tecnologias Core**| Python, Flask (Backend), HTML/CSS/JavaScript (Frontend), API de IA (Geralmente Google Gemini ou similar), Reconhecimento de Voz (Webkit). |
| **Status Atual** | Funcionalidades críticas estáveis (Chat, UI Responsiva, Voz, Envio de Mensagens e Saudação). |

---

## 2. Arquitetura e Estrutura de Arquivos

O projeto segue a estrutura padrão de uma aplicação Flask.

. ├── app.py # Lógica principal do Flask e rotas ├── requirements.txt # Dependências do Python (Flask, Gunicorn, etc.) ├── templates/ │ └── chat_interface.html # Frontend principal (Interface do Chat) └── static/ ├── style.css # Estilos de todas as versões (V60.52 é a última estável de layout) ├── script.js # Lógica de Interação do Frontend (V60.55 é a última funcional) └── sua-logo.png # Imagem da Logo da Igreja

---

## 3. Funcionalidades Implementadas e Status

| Funcionalidade | Implementação/Status | Arquivo Envolvido | Versão de Estabilidade |
| :--- | :--- | :--- | :--- |
| **Interface Responsiva** | Layout adaptado para Desktop e Mobile (corrigido o corte horizontal). | `style.css` | V60.52 |
| **Saudação Inicial** | Mensagem de boas-vindas da IA é exibida ao carregar a página. | `script.js`, `chat_interface.html` | V60.50 |
| **Placeholder do Input**| Texto correto: "Peça à Hope..." | `chat_interface.html` | V60.49 |
| **Largura do Input** | Campo de pesquisa preenche corretamente a largura do container. | `style.css` | V60.52 |
| **Envio de Mensagem** | Envio de texto via `Enter` ou botão Enviar. | `script.js` | V60.54 |
| **Reconhecimento de Voz**| Utiliza `webkitSpeechRecognition` para transcrição em Português (pt-BR). | `script.js` | V60.53 |
| **Envio Automático de Voz**| Transcrição de áudio é enviada automaticamente após a conclusão da fala. | `script.js` | V60.55 |
| **Aviso Legal** | Aviso sobre possíveis erros da IA visível na parte inferior. | `style.css` | V60.51 |
| **Formato de Mensagens**| Suporte para **negrito** (Markdown/WhatsApp) e elementos de botão (links de ação). | `script.js` | V60.45 (Base) |

---

## 4. Componentes Chave do Código (Versões Finais)

### 4.1. Configuração do Frontend (`templates/chat_interface.html`)

O HTML foca em passar a variável de saudação de forma segura para o JavaScript.

```html
<script>
    // CRÍTICO: Define a variável JS com o valor do Flask/Jinja
    const INITIAL_SAUDACAO_TEXT = "{{ saudacao | safe }}"; 
</script>

<form id="chat-form">
    <div id="input-wrapper">
        <textarea id="pergunta-input" placeholder="Peça à Hope..." rows="1"></textarea>
        <button type="button" id="microphone-btn" class="icon-btn" disabled>
            <i class="fas fa-microphone"></i>
        </button>
        </div>
</form>



4.2. Estilização e Layout (static/style.css - V60.52)


/* V60.52: Correção de Layout e Largura do Input */
.chat-input-container {
    padding: 10px 20px 5px; /* Alinhamento e espaçamento reduzido */
}

#input-wrapper {
    padding: 0; /* Remoção do padding horizontal que causava o corte */
}

#pergunta-input {
    width: 100%;
    box-sizing: border-box; /* Crucial para o cálculo da largura total */
}

.aviso-inferior {
    padding: 10px 20px 70px; /* Redução do espaçamento superior */
}



4.3. Lógica do Frontend (static/script.js - V60.55)

document.addEventListener('DOMContentLoaded', function() {
    const microphoneBtn = document.getElementById('microphone-btn'); 
    const form = document.getElementById('chat-form');
    const input = document.getElementById('pergunta-input');
    // ... (Outras declarações) ...

    // 1. Saudação (V60.50)
    if (typeof INITIAL_SAUDACAO_TEXT !== 'undefined' && INITIAL_SAUDACAO_TEXT.trim() !== '') {
        appendMessage(INITIAL_SAUDACAO_TEXT, 'ia');
    }

    // 2. Lógica de Reconhecimento de Voz (V60.55)
    if ('webkitSpeechRecognition' in window) {
        microphoneBtn.disabled = false;
        const recognition = new webkitSpeechRecognition();
        // ... (Configurações e Eventos) ...
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            // CRÍTICO V60.55: Envio automático após a transcrição
            form.dispatchEvent(new Event('submit')); 
        };
    } else {
        microphoneBtn.style.display = 'none';
    }

    // 3. Lógica de Envio do Formulário (V60.54)
    form.addEventListener('submit', async function(e) {
        // ... (Lógica de fetch /api/chat) ...
    });
    
    // 4. Envio via ENTER
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); 
            form.dispatchEvent(new Event('submit'));
        }
    });
});



5. Histórico de Versões (Resumo das Correções)


Versão,Descrição,Status
V60.49,"Corrigiu o placeholder (""Peça à Hope..."") e tentou a primeira correção de largura do input.",Layout Incompleto
V60.50,Restaurou a Saudação Inicial (resolvendo o problema de interpolação Jinja/JS).,Layout Incompleto
V60.51,Redução do espaçamento Input/Aviso.,Layout Cortado
V60.52,ESTÁVEL LAYOUT: Corrigiu o corte horizontal do input (ajuste de padding e box-sizing).,Funcionalidades Parcial
V60.53,Restaurou a funcionalidade do Microfone (habilitação e lógica webkitSpeechRecognition).,Envio Parcial
V60.54,Restaurou o envio de Mensagens de Texto e a execução da Saudação (corrigindo erros de sintaxe JS).,Envio Áudio Pendente
V60.55,ESTÁVEL FUNCIONAL: Restaurou o envio automático da transcrição de áudio.,TUDO FUNCIONANDO



