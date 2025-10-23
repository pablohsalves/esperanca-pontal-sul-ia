// script.js - VERSÃO V60.11 (Ajuste da Lógica UI/UX)

document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('pergunta-input');
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');

    let isThinking = false; // Flag para controlar o estado da IA

    // --- Funções de Ajuda UI ---

    // 1. Gerencia a visibilidade dos botões
    function updateButtonVisibility() {
        const hasText = input.value.trim().length > 0;
        
        if (isThinking) {
            // IA está pensando: O Microfone some e o Enviar se torna o Stop
            microphoneBtn.style.display = 'none';
            enviarBtn.style.display = 'flex'; 
            enviarBtn.disabled = false; 
            enviarBtn.innerHTML = '<i class="fas fa-stop"></i>'; 
            enviarBtn.title = 'Parar Resposta';
        } else if (hasText) {
            // Tem texto: O Microfone some e o Enviar é o avião (habilitado)
            microphoneBtn.style.display = 'none';
            enviarBtn.style.display = 'flex'; 
            enviarBtn.disabled = false;
            enviarBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            enviarBtn.title = 'Enviar Mensagem';
        } else {
            // Sem texto: Mostra o Microfone e desabilita o Enviar (avião)
            microphoneBtn.style.display = 'flex'; 
            enviarBtn.style.display = 'flex'; 
            enviarBtn.disabled = true;
            enviarBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            enviarBtn.title = 'Digite uma mensagem';
        }
    }

    // 2. Cria uma nova bolha de mensagem
    function createMessage(texto, tipo) {
        const mensagemDiv = document.createElement('div');
        mensagemDiv.classList.add('mensagem', tipo);
        
        const htmlContent = texto.replace(/\n\n/g, '<p>').replace(/\n/g, '<br>');
        mensagemDiv.innerHTML = htmlContent;
        chatBox.appendChild(mensagemDiv);
        
        chatBox.scrollTop = chatBox.scrollHeight;
        return mensagemDiv;
    }

    // 3. Gerencia o "Digitando..." da IA
    function showTypingIndicator() {
        if (!document.getElementById('typing-indicator')) {
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.classList.add('mensagem', 'ia');
            typingDiv.innerHTML = 'Digitando...';
            chatBox.appendChild(typingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    // 4. Remove o "Digitando..." da IA
    function removeTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    // 5. Ajusta a altura da caixa de texto
    function autoResize() {
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px'; 
    }

    // --- Lógica Principal do Chat ---

    async function sendMessage() {
        const userMessage = input.value.trim();
        if (userMessage === '') return;

        // 1. Estado de envio
        isThinking = true;
        updateButtonVisibility(); 
        input.disabled = true; 

        // 2. Adiciona a mensagem do usuário
        createMessage(userMessage, 'usuario');
        
        // 3. Mostra o indicador de digitação
        showTypingIndicator();

        // 4. Limpa e reseta o input
        input.value = '';
        autoResize(); 
        updateButtonVisibility(); 

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mensagem: userMessage }),
            });

            if (!isThinking) return;

            const data = await response.json();
            
            // 5. Remove o indicador de digitação
            removeTypingIndicator();
            
            // 6. Adiciona a resposta da IA
            createMessage(data.resposta, 'ia');
            
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            removeTypingIndicator();
            createMessage('Desculpe, ocorreu um erro de conexão. Por favor, tente novamente.', 'ia');
        } finally {
            // 7. Volta ao estado normal
            isThinking = false;
            input.disabled = false;
            updateButtonVisibility();
            input.focus();
        }
    }
    
    // Lógica de Stop (apenas front-end)
    function stopResponse() {
        if (isThinking) {
            console.log("Comando de Parada de Resposta acionado (apenas UI).");
            
            removeTypingIndicator();
            isThinking = false;
            input.disabled = false;
            updateButtonVisibility();
            
            createMessage("A resposta foi interrompida, mas a IA continua pronta para conversar.", 'ia');
            input.focus();
        }
    }


    // --- Event Listeners ---
    
    // Enviar mensagem ao clicar no avião/stop
    enviarBtn.addEventListener('click', () => {
        if (isThinking) {
            stopResponse();
        } else {
            sendMessage();
        }
    });

    // Enviar mensagem ao pressionar ENTER
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); 
            if (isThinking) {
                stopResponse();
            } else {
                sendMessage();
            }
        }
    });

    // Atualiza a visibilidade dos botões e a altura da caixa ao digitar
    input.addEventListener('input', () => {
        updateButtonVisibility();
        autoResize();
    });

    // Garante que o estado inicial é carregado corretamente
    updateButtonVisibility();
    autoResize(); 
});