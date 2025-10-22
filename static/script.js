// static/script.js - Versão FINAL com Chips Dinâmicos

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    let singleRowHeight = 0; 
    let recognition = null; 

    // Inicializa a rolagem
    rolarParaBaixo(); 

    function rolarParaBaixo() {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }
    
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            singleRowHeight = input.scrollHeight;
        }
        
        input.style.height = 'auto'; 
        input.style.height = input.scrollHeight + 'px';
        
        rolarParaBaixo();
    }
    
    input.addEventListener('input', autoExpand);
    autoExpand(); 

    function adicionarMensagem(texto, remetente) {
        const div = document.createElement('div');
        div.className = `mensagem ${remetente}`;
        const htmlContent = texto.replace(/\n/g, '<br>');
        div.innerHTML = htmlContent;
        chatBox.appendChild(div);
        rolarParaBaixo();
        return div;
    }

    async function enviarMensagem() {
        const pergunta = input.value.trim();
        
        if (pergunta === '') { return; }

        // Remove os chips de sugestão do topo ao enviar a primeira pergunta
        const suggestionChips = document.querySelector('.suggestion-chips');
        if (suggestionChips) {
            suggestionChips.style.display = 'none';
        }

        // 1. Exibe a mensagem do usuário
        adicionarMensagem(pergunta, 'usuario');
        
        // 2. Reseta o input e desabilita
        input.value = ''; 
        input.style.height = singleRowHeight + 'px';
        
        input.disabled = true;
        enviarBtn.disabled = true;

        // 3. Adiciona o indicador de carregamento (Pensando...)
        const loadingDiv = adicionarMensagem('<span class="loading-indicator"></span>Pensando...', 'ia');

        try {
            // 4. Envia a requisição para o endpoint /api/chat
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
            
            // 5. Remove o indicador de carregamento
            chatBox.removeChild(loadingDiv);
            
            // 6. Exibe a resposta final da IA
            adicionarMensagem(data.resposta, 'ia');

        } catch (error) {
            if(loadingDiv.parentNode) {
                chatBox.removeChild(loadingDiv);
            }
            console.error('Erro ao enviar mensagem:', error);
            let erroDisplay = error.message;
            if (erroDisplay.includes('Erro HTTP: 500')) {
                erroDisplay = "Erro do Servidor Interno. Tente recarregar a página.";
            } else if (erroDisplay.includes('Failed to fetch')) {
                erroDisplay = "Erro de conexão: Não foi possível alcançar o servidor.";
            }
            adicionarMensagem(`Erro: ${erroDisplay}`, 'ia');
            
        } finally {
            // 7. Reabilita e foca
            input.disabled = false;
            enviarBtn.disabled = false;
            input.focus();
            rolarParaBaixo();
        }
    }
    
    // --- Lógica de Reconhecimento de Fala (Web Speech API) ---
    // (O código de Voz é mantido, mas omitido aqui por brevidade)
    
    // --- Ativar o envio por Enter e Clique (Campo de texto) ---
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            enviarMensagem();
        }
    });

    enviarBtn.addEventListener('click', enviarMensagem);
    
    // --- Lógica para Chips/Botões Clicáveis (Chat Box e Sugestões) ---
    chatBox.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip');
        if (chip) {
            const url = chip.getAttribute('data-url');
            const isSuggestion = chip.classList.contains('suggestion-chip');
            
            if (url && !isSuggestion) {
                // Se for um chip de resposta da IA, abre em nova aba
                window.open(url, '_blank');
            }
            
            if (isSuggestion) {
                 // Se for um chip de sugestão, coloca o texto no input e envia
                 const text = chip.getAttribute('data-text');
                 
                 // Se for um link de navegação interno, apenas navega (ex: Horários)
                 if (url.startsWith('/')) {
                     window.location.href = url;
                 } else {
                    // Para todos os outros, assume que é uma pergunta
                    input.value = `Qual é o ${text.toLowerCase()} da igreja?`;
                    autoExpand();
                    enviarMensagem();
                 }
            }
        }
    });
});