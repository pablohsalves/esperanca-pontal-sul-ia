// script.js - VERSÃO V60.18 (Processamento de Resposta com Botão de Contato e Voz Direta)

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
            
            // Transcrição de Voz: Envia a mensagem DIRETAMENTE
            if (transcript.trim() !== '') {
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

    // 2. CRÍTICO V60.18: Cria uma bolha de mensagem (agora pode criar botões)
    function createMessage(content, tipo) {
        const mensagemDiv = document.createElement('div');
        mensagemDiv.classList.add('mensagem', tipo);
        
        // Verifica se o conteúdo é um objeto (resposta estruturada do backend)
        if (typeof content === 'object' && content.type === 'button') {
            const wrapperDiv = document.createElement('div');
            wrapperDiv.classList.add('ia-action-button');

            // 1. Texto de introdução (usando innerHTML para permitir o Markdown que vem do Flask)
            const preText = document.createElement('p');
            preText.innerHTML = content.pre_text;
            wrapperDiv.appendChild(preText);

            // 2. Botão Clicável (Link)
            const buttonLink = document.createElement('a');
            buttonLink.classList.add('button-link');
            buttonLink.href = content.button_url;
            buttonLink.target = '_blank'; // Abrir em nova aba

            // Ícone + Texto do Botão
            buttonLink.innerHTML = `<i class="${content.button_icon}"></i> ${content.button_text}`;
            wrapperDiv.appendChild(buttonLink);
            
            mensagemDiv.appendChild(wrapperDiv);

        } else {
            // Se for string ou objeto tipo 'text' (resposta normal da IA)
            const textContent = (typeof content === 'string') ? content : content.resposta;
            const htmlContent = textContent.replace(/\n\n/g, '<p>').replace(/\n/g, '<br>');
            mensagemDiv.innerHTML = htmlContent;
        }
        
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

    async function sendMessage(messageToSend = null) {
        const userMessage = messageToSend || input.value.trim();
        
        if (userMessage === '') return;

        isThinking = true;
        updateButtonVisibility(); 
        input.disabled = true; 

        createMessage(userMessage, 'usuario');
        
        showTypingIndicator();

        if (!messageToSend) {
            input.value = '';
        }
        autoResize(); 

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
            
            removeTypingIndicator();
            
            // Envia o objeto JSON completo (data) para o createMessage
            createMessage(data, 'ia');
            
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            removeTypingIndicator();
            createMessage({"resposta": "Desculpe, ocorreu um erro de conexão. Por favor, tente novamente."}, 'ia');
        } finally {
            isThinking = false;
            input.disabled = false;
            updateButtonVisibility();
            input.focus();
        }
    }
    
    // Lógica de Stop 
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

    // Inicia/Para o Reconhecimento de Fala 
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