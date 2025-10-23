// static/script.js - Versão FINAL E FUNCIONAL (FINAL ESTÁVEL)

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    console.log("script.js carregado e event listeners anexados.");

    if (!input || !enviarBtn || !microphoneBtn || !chatBox) {
        console.error("ERRO CRÍTICO JS: Elementos essenciais não encontrados. O envio não funcionará.");
        return; 
    }
    
    let singleRowHeight = 0; 
    let recognition = null; 
    
    // --- FUNÇÕES DE ESTADO E UTILS ---
    
    function resetarEstadoInput() {
        input.disabled = false;
        microphoneBtn.disabled = false;
        enviarBtn.disabled = input.value.trim() === ''; 
    }

    function rolarParaBaixo() {
        setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }, 50); 
    }
    
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            singleRowRowHeight = input.scrollHeight; 
            input.style.height = singleRowHeight + 'px';
        }
        
        input.style.height = 'auto'; 
        input.style.height = input.scrollHeight + 'px'; 
        
        enviarBtn.disabled = input.value.trim() === '';
        
        rolarParaBaixo();
    }
    
    function adicionarMensagem(texto, remetente) {
        const div = document.createElement('div');
        div.className = `mensagem ${remetente}`;
        div.innerHTML = texto; 
        chatBox.appendChild(div);
        rolarParaBaixo();
        return div;
    }

    // --- FUNÇÃO PRINCIPAL DE ENVIO ---
    async function enviarMensagem() {
        console.log('EVENTO DE ENVIO DISPARADO.'); 
        
        const pergunta = input.value.trim();
        
        if (pergunta === '') { 
             console.log('Pergunda vazia. Retornando imediatamente.');
             resetarEstadoInput(); 
             return; 
        }

        const suggestionChipsContainer = document.querySelector('.suggestion-chips');
        if (suggestionChipsContainer) {
            suggestionChipsContainer.style.display = 'none'; 
        }

        adicionarMensagem(pergunta, 'usuario'); 
        
        input.value = ''; 
        input.style.height = singleRowHeight + 'px';
        
        input.disabled = true;
        enviarBtn.disabled = true;
        microphoneBtn.disabled = true;

        rolarParaBaixo(); 

        const loadingDiv = adicionarMensagem('<span class="loading-indicator"></span>Esperança está processando...', 'ia');

        try {
            console.log(`Enviando POST para /api/chat com a pergunta: "${pergunta}"`);
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pergunta: pergunta })
            });

            if (!response.ok) {
                console.error(`Resposta HTTP não OK: ${response.status}`);
                const errorData = await response.json().catch(() => ({ erro: 'Erro de comunicação desconhecido.' }));
                throw new Error(errorData.erro || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            
            if(loadingDiv.parentNode) {
                chatBox.removeChild(loadingDiv);
            }
            adicionarMensagem(data.resposta, 'ia'); 

        } catch (error) {
            if(loadingDiv.parentNode) {
                chatBox.removeChild(loadingDiv);
            }
            console.error('ERRO FATAL NO FETCH:', error);
            let erroDisplay = error.message;
            if (erroDisplay.includes('Erro HTTP') || erroDisplay.includes('from_dict')) {
                erroDisplay = `Erro do Servidor. (Falha de IA resolvida no Backend - verifique logs).`;
            } else if (erroDisplay.includes('Failed to fetch')) {
                erroDisplay = "Erro de conexão: Não foi possível alcançar o servidor.";
            }
            adicionarMensagem(`<p style="color: #ff5555;">Erro: ${erroDisplay}</p>`, 'ia'); 
            
        } finally {
            resetarEstadoInput(); 
            input.focus();
            rolarParaBaixo();
        }
    }
    
    // --- LÓGICA DE EVENT LISTENERS ---
    
    // 1. INPUT/ENVIAR (Teclado e Clique)
    input.addEventListener('input', autoExpand);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            enviarMensagem();
        }
    });
    enviarBtn.addEventListener('click', enviarMensagem);
    
    // 2. MICROFONE (Reconhecimento de voz)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'pt-BR'; 
        recognition.interimResults = false; 
        recognition.maxAlternatives = 1;

        microphoneBtn.addEventListener('click', () => {
            if (microphoneBtn.classList.contains('recording')) {
                recognition.stop();
            } else {
                try {
                    recognition.start();
                } catch (e) {
                    console.warn("Reconhecimento de voz já ativo.", e);
                }
            }
        });

        recognition.onstart = () => {
            microphoneBtn.classList.add('recording');
            microphoneBtn.style.color = '#ff5555'; 
            input.placeholder = 'Escutando... Fale agora.';
            input.disabled = true;
            enviarBtn.disabled = true; 
        };

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            input.value = speechResult;
        };

        recognition.onend = () => {
            microphoneBtn.classList.remove('recording');
            microphoneBtn.style.color = 'var(--color-highlight)';
            input.placeholder = 'Peça à Esperança';
            
            if (input.value.trim() !== '') {
                enviarMensagem();
            } else {
                resetarEstadoInput(); 
            }
        };

        recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de voz:', event.error);
            recognition.onend(); 
            if (event.error === 'not-allowed') {
                 alert('Acesso ao microfone negado. Verifique as permissões do seu navegador.');
            } 
        };

    } else {
        microphoneBtn.style.display = 'none';
    }
    
    // 3. CHIPS CLICÁVEIS 
    chatBox.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip'); 
        if (chip) {
            const url = chip.getAttribute('data-url');
            const isSuggestion = chip.classList.contains('suggestion-chip');
            
            if (url) {
                if (!isSuggestion) {
                    e.preventDefault(); 
                    window.open(url, '_blank');
                    return;
                } 
                else {
                    const text = chip.getAttribute('data-text');
                    
                    let perguntaSugerida = text;
                    if (text.includes("WhatsApp")) {
                         perguntaSugerida = "Qual é o número de WhatsApp da igreja?";
                    } else if (text.includes("Mapa") || text.includes("Localização")) {
                         perguntaSugerida = "Onde fica a igreja (endereço completo)?";
                    } else if (text.includes("Horários")) {
                         perguntaSugerida = "Quais são os horários dos cultos?";
                    }
                    
                    input.value = perguntaSugerida;
                    autoExpand();
                    enviarMensagem(); 
                }
            }
        }
    });
    
    // Inicialização final do estado
    resetarEstadoInput();
    rolarParaBaixo();
});