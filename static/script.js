// static/script.js - Versão FINAL E ESTÁVEL com Rolagem, Chips e Microfone (Revisão V7)

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    let singleRowHeight = 0; 
    let recognition = null; 
    
    // --- FUNÇÕES DE ESTADO INICIAL ---
    
    function resetarEstadoInput() {
        // Garante que o input e botões estejam habilitados (estado padrão)
        input.disabled = false;
        microphoneBtn.disabled = false;
        
        // CRÍTICO: O botão de enviar só é ativado se houver texto
        enviarBtn.disabled = input.value.trim() === '';
    }

    // Inicializa o estado dos botões ao carregar a página
    resetarEstadoInput();

    // --- ROLAGEM E AUTOSIZE ---
    function rolarParaBaixo() {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
    
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            singleRowHeight = input.scrollHeight; 
            input.style.height = singleRowHeight + 'px';
        }
        
        input.style.height = 'auto'; 
        input.style.height = input.scrollHeight + 'px'; 
        
        // CRÍTICO: Ativa/Desativa o botão de envio em tempo real
        enviarBtn.disabled = input.value.trim() === '';
        
        rolarParaBaixo();
    }
    
    input.addEventListener('input', autoExpand);
    setTimeout(autoExpand, 0); 
    rolarParaBaixo(); 


    // --- FUNÇÃO DE MENSAGEM ---
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
        const pergunta = input.value.trim();
        
        if (pergunta === '') { return; }

        const suggestionChipsContainer = document.querySelector('.suggestion-chips');
        if (suggestionChipsContainer) {
            suggestionChipsContainer.style.display = 'none'; 
        }

        // 1. Exibe a mensagem do usuário
        adicionarMensagem(pergunta, 'usuario'); 
        
        // 2. Desabilita todos os inputs
        input.value = ''; 
        input.style.height = singleRowHeight + 'px';
        
        input.disabled = true;
        enviarBtn.disabled = true;
        microphoneBtn.disabled = true;

        rolarParaBaixo(); 

        // 3. Adiciona o indicador de carregamento
        const loadingDiv = adicionarMensagem('<span class="loading-indicator"></span>Esperança está processando...', 'ia');

        try {
            // 4. Envia a requisição
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pergunta: pergunta })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ erro: 'Erro de comunicação desconhecido.' }));
                throw new Error(errorData.erro || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            
            // 5. Remove o indicador
            if(loadingDiv.parentNode) {
                chatBox.removeChild(loadingDiv);
            }
            
            // 6. Exibe a resposta final da IA
            adicionarMensagem(data.resposta, 'ia'); 

        } catch (error) {
            if(loadingDiv.parentNode) {
                chatBox.removeChild(loadingDiv);
            }
            console.error('Erro ao enviar mensagem:', error);
            let erroDisplay = error.message;
            if (erroDisplay.includes('Erro HTTP')) {
                erroDisplay = "Erro do Servidor. Tente recarregar a página ou verifique o log de IA.";
            } else if (erroDisplay.includes('Failed to fetch')) {
                erroDisplay = "Erro de conexão: Não foi possível alcançar o servidor.";
            }
            adicionarMensagem(`<p>Erro: ${erroDisplay}</p>`, 'ia'); 
            
        } finally {
            // 7. Reabilita o estado e foca
            resetarEstadoInput(); // Usa a nova função para resetar o estado
            input.focus();
            rolarParaBaixo();
        }
    }
    
    // --- LÓGICA DE RECONHECIMENTO DE FALA (MICROFONE) ---

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
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
                    console.warn("Reconhecimento de voz já ativo ou falha ao iniciar.", e);
                }
            }
        });

        recognition.onstart = () => {
            microphoneBtn.classList.add('recording');
            microphoneBtn.style.color = '#ff5555'; // Vermelho
            input.placeholder = 'Escutando... Fale agora.';
            input.disabled = true;
            enviarBtn.disabled = true; // Desabilita o envio durante a gravação
        };

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            input.value = speechResult;
            enviarMensagem(); 
        };

        recognition.onend = () => {
            microphoneBtn.classList.remove('recording');
            microphoneBtn.style.color = 'var(--color-highlight)';
            input.placeholder = 'Peça à Esperança';
            resetarEstadoInput(); // Usa a nova função para resetar o estado
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
    
    // --- Lógica de Envio (Enter e Clique) ---
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            enviarMensagem();
        }
    });

    enviarBtn.addEventListener('click', enviarMensagem);
    
    // --- Lógica para Chips/Botões Clicáveis ---
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

                    // Lógica para montar a pergunta sugerida (mantida)
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
});