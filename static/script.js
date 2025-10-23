// script.js - VERSÃO V60.17 (Transcrição de Voz Direta para Envio)

document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('pergunta-input');
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');

    let isThinking = false; 
    let recognition = null; 
    let isListening = false; 

    // --- Inicialização da API de Reconhecimento de Fala ---
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false; 
        recognition.interimResults = false; 
        recognition.lang = 'pt-BR'; 

        recognition.onstart = function() {
            isListening = true;
            microphoneBtn.classList.add('mic-active'); 
            microphoneBtn.innerHTML = '<i class="fas fa-microphone-alt-slash"></i>'; 
            input.placeholder = "Escutando... Fale agora...";
            input.focus();
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            
            // CRÍTICO V60.17: Envia a transcrição DIRETAMENTE como mensagem do usuário
            if (transcript.trim() !== '') {
                // Chama a função de envio com o texto transcrito
                sendMessage(transcript.trim()); 
            }
        };

        recognition.onerror = function(event) {
            console.error('Erro de reconhecimento de fala: ', event.error);
            alert(`Erro ao tentar usar o microfone: ${event.error}. Certifique-se de que o navegador tem permissão.`);
            stopListening();
        };

        recognition.onend = function() {
            stopListening();
        };
    } else {
        microphoneBtn.style.display = 'none';
        console.warn("A API de Reconhecimento de Fala do navegador não é suportada.");
    }
    
    // Função para parar a escuta
    function stopListening() {
        if (recognition && isListening) {
            recognition.stop();
        }
        isListening = false;
        microphoneBtn.classList.remove('mic-active');
        microphoneBtn.innerHTML = '<i class="fas fa-microphone"></i>'; 
        input.placeholder = "Peça à Esperança...";
        updateButtonVisibility();
    }


    // --- Funções de Ajuda UI ---

    // (As funções updateButtonVisibility, createMessage, show/removeTypingIndicator e autoResize permanecem as mesmas da V60.16)
    
    // 1. Gerencia a visibilidade dos botões
    function updateButtonVisibility() {
        const hasText = input.value.trim().length > 0;
        
        if (isThinking) {
            microphoneBtn.style.display = 'none';
            enviarBtn.style.display = 'flex'; 
            enviarBtn.disabled = false; 
            enviarBtn.innerHTML = '<i class="fas fa-stop"></i>'; 
            enviarBtn.title = 'Parar Resposta';
        } else if (hasText) {
            microphoneBtn.style.display = 'none';
            enviarBtn.style.display = 'flex'; 
            enviarBtn.disabled = false;
            enviarBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            enviarBtn.title = 'Enviar Mensagem';
        } else {
            if (recognition) {
                 microphoneBtn.style.display = 'flex'; 
            } else {
                 microphoneBtn.style.display = 'none';
            }
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

    // CRÍTICO V60.17: Função agora aceita um parâmetro (userMessage)
    async function sendMessage(messageToSend = null) {
        // Usa a mensagem passada como parâmetro OU o conteúdo da caixa de input
        const userMessage = messageToSend || input.value.trim();
        
        if (userMessage === '') return;

        // 1. Estado de envio
        isThinking = true;
        updateButtonVisibility(); 
        input.disabled = true; 

        // 2. Adiciona a mensagem do usuário
        createMessage(userMessage, 'usuario');
        
        // 3. Mostra o indicador de digitação
        showTypingIndicator();

        // 4. Limpa e reseta o input (Apenas se não foi enviado diretamente do input)
        if (!messageToSend) {
            input.value = '';
        }
        autoResize(); 
        // updateButtonVisibility() aqui não é estritamente necessário se o input foi limpo

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
    
    // Lógica de Stop (mantida)
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
    
    // Enviar mensagem ao clicar no avião/stop (mantida)
    enviarBtn.addEventListener('click', () => {
        if (isThinking) {
            stopResponse();
        } else {
            // Envia o conteúdo do input
            sendMessage();
        }
    });

    // Inicia/Para o Reconhecimento de Fala (mantida)
    microphoneBtn.addEventListener('click', () => {
        if (!recognition) {
             alert("A função de voz não é suportada ou não foi ativada neste navegador.");
             return;
        }

        if (isListening) {
            stopListening();
        } else {
            try {
                recognition.start();
            } catch (e) {
                if (e.name !== 'InvalidStateError') {
                    console.error("Erro ao iniciar reconhecimento de fala: ", e);
                }
            }
        }
        input.focus();
    });

    // Enviar mensagem ao pressionar ENTER (mantida)
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); 
            if (isThinking) {
                stopResponse();
            } else {
                // Envia o conteúdo do input
                sendMessage();
            }
        }
    });

    // Atualiza a visibilidade dos botões e a altura da caixa ao digitar (mantida)
    input.addEventListener('input', () => {
        updateButtonVisibility();
        autoResize();
    });

    // Garante que o estado inicial é carregado corretamente
    updateButtonVisibility();
    autoResize(); 
});