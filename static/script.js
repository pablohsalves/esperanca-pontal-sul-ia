// static/script.js - Versão V29.0 (Completo com layout dinâmico e botões ajustados)

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('pergunta-input');
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');

    // Inicialização da visibilidade dos botões
    microphoneBtn.style.display = 'flex';
    enviarBtn.style.display = 'none';
    enviarBtn.disabled = true; 

    // ----------------------------------------------------
    // FUNÇÕES DE UTILIDADE
    // ----------------------------------------------------

    function rolarParaBaixo() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function criarMensagem(texto, remetente) {
        const mensagemDiv = document.createElement('div');
        mensagemDiv.classList.add('mensagem', remetente);
        mensagemDiv.innerHTML = texto;
        chatBox.appendChild(mensagemDiv);
        rolarParaBaixo();
    }

    function criarLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('mensagem', 'ia', 'loading-indicator');
        loadingDiv.innerHTML = '<div class="typing-dots"><span>.</span><span>.</span><span>.</span></div>';
        chatBox.appendChild(loadingDiv);
        rolarParaBaixo();
        return loadingDiv;
    }
    
    // ----------------------------------------------------
    // LÓGICA DE INPUT (EXPANSÃO E BOTÕES DINÂMICOS)
    // ----------------------------------------------------

    function autoExpand() {
        // Redefine a altura para calcular o scrollHeight
        input.style.height = 'auto'; 
        // Define a nova altura, limitada pelo CSS max-height
        input.style.height = input.scrollHeight + 'px'; 
        
        const isInputEmpty = input.value.trim() === '';

        // Lógica de Visibilidade: MIC vs. Avião
        if (isInputEmpty) {
            // Input vazio: Mostra MIC, Esconde Avião
            microphoneBtn.style.display = 'flex'; 
            enviarBtn.style.display = 'none'; 
            enviarBtn.disabled = true;
            // CRÍTICO: Ajusta o padding-right para evitar que o texto do input seja coberto pelo MIC
            input.style.paddingRight = '60px'; 
        } else {
            // Input com texto: Esconde MIC, Mostra Avião
            microphoneBtn.style.display = 'none'; 
            enviarBtn.style.display = 'flex'; 
            enviarBtn.disabled = false;
            // CRÍTICO: Ajusta o padding-right para evitar que o texto do input seja coberto pelo Avião
            input.style.paddingRight = '60px'; 
        }

        rolarParaBaixo();
    }

    input.addEventListener('input', autoExpand);
    window.addEventListener('resize', autoExpand); 


    // ----------------------------------------------------
    // LÓGICA DE ENVIO DE MENSAGEM
    // ----------------------------------------------------

    async function enviarMensagem() {
        const pergunta = input.value.trim();
        if (!pergunta) return;

        // 1. Desabilita input e botões
        input.disabled = true;
        enviarBtn.disabled = true;
        microphoneBtn.disabled = true;

        // 2. Adiciona a mensagem do usuário
        criarMensagem(pergunta, 'usuario');
        input.value = ''; 
        autoExpand();     

        // 3. Adiciona indicador de carregamento
        const loadingIndicator = criarLoadingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pergunta: pergunta })
            });

            if (!response.ok) {
                throw new Error(`Erro de rede: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            // 4. Remove indicador e mostra resposta
            chatBox.removeChild(loadingIndicator);
            
            if (data.erro || data.resposta.includes("Erro Interno")) {
                 criarMensagem(`**Erro:** ${data.erro || data.resposta}`, 'ia');
            } else {
                 criarMensagem(data.resposta, 'ia');
            }

        } catch (error) {
            console.error('Falha ao enviar mensagem:', error);
            if (chatBox.contains(loadingIndicator)) {
                chatBox.removeChild(loadingIndicator);
            }
            criarMensagem(`Desculpe, não consegui me comunicar com o servidor. (${error.message})`, 'ia');

        } finally {
            // 5. Reabilita input e botões
            input.disabled = false;
            microphoneBtn.disabled = false;
            autoExpand(); 
            input.focus(); 
        }
    }

    // Eventos de click e tecla
    enviarBtn.addEventListener('click', enviarMensagem);
    
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); 
            enviarMensagem();
        }
    });

    // ----------------------------------------------------
    // INICIALIZAÇÃO
    // ----------------------------------------------------

    autoExpand(); 
});