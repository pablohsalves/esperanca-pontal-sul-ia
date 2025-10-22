// static/script.js - Versão FINAL com Textarea Auto-Expansível e Microfone

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input'); 
    const enviarBtn = document.getElementById('enviar-btn');
    const microphoneBtn = document.getElementById('microphone-btn');
    const chatBox = document.getElementById('chat-box');
    
    let singleRowHeight = 0; 
    let recognition = null; // Variável para a API de reconhecimento de fala

    // Inicializa a rolagem para a mensagem inicial (saudação)
    rolarParaBaixo(); 

    // Função para rolar para a mensagem mais recente
    function rolarParaBaixo() {
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    // Função para ajustar a altura da textarea
    function autoExpand() {
        if (singleRowHeight === 0) {
            input.style.height = 'auto';
            singleRowHeight = input.scrollHeight;
        }
        
        input.style.height = 'auto'; 
        input.style.height = input.scrollHeight + 'px';
        
        rolarParaBaixo();
    }
    
    // Ouve a digitação e cola para redimensionar
    input.addEventListener('input', autoExpand);
    
    // Garante que o input comece com a altura correta (1 linha)
    autoExpand(); 


    // Função para adicionar uma nova bolha de mensagem ao chat
    function adicionarMensagem(texto, remetente) {
        const div = document.createElement('div');
        div.className = `mensagem ${remetente}`;
        
        const htmlContent = texto.replace(/\n/g, '<br>');
        
        div.innerHTML = htmlContent;
        chatBox.appendChild(div);
        rolarParaBaixo();
        return div;
    }

    // Função principal para enviar a mensagem ao backend (Flask/Render)
    async function enviarMensagem() {
        const pergunta = input.value.trim();
        
        if (pergunta === '') {
            return; 
        }

        // 1. Exibe a mensagem do usuário imediatamente
        adicionarMensagem(pergunta, 'usuario');
        
        // 2. Reseta o input para o estado inicial (1 linha)
        input.value = ''; 
        input.style.height = singleRowHeight + 'px'; // Reseta a altura para 1 linha
        
        // Desabilita o input e o botão
        input.disabled = true;
        enviarBtn.disabled = true;

        // 3. Adiciona um indicador visual de carregamento da IA
        const loadingDiv = adicionarMensagem('Digitando...', 'ia');

        try {
            // 4. Envia a requisição para o endpoint /api/chat
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pergunta: pergunta })
            });

            // 5. Verifica a resposta
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ erro: 'Erro de comunicação desconhecido.' }));
                throw new Error(errorData.erro || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();

            // 6. Remove o indicador de carregamento
            chatBox.removeChild(loadingDiv);

            // 7. Exibe a resposta da IA
            adicionarMensagem(data.resposta, 'ia');

        } catch (error) {
            // Trata erros de servidor ou conexão
            chatBox.removeChild(loadingDiv);
            console.error('Erro ao enviar mensagem:', error);
            
            let erroDisplay = error.message;
            if (erroDisplay.includes('Erro HTTP: 500')) {
                erroDisplay = "Erro do Servidor Interno. Tente recarregar a página.";
            } else if (erroDisplay.includes('Failed to fetch')) {
                erroDisplay = "Erro de conexão: Não foi possível alcançar o servidor.";
            }

            adicionarMensagem(`Erro: ${erroDisplay}`, 'ia');
        } finally {
            // 8. Reabilita o input e o botão
            input.disabled = false;
            enviarBtn.disabled = false;
            input.focus();
            rolarParaBaixo();
        }
    }
    
    // --- Lógica de Reconhecimento de Fala (Web Speech API) ---

    // Função auxiliar para pegar variáveis CSS
    function varToCSS(varName) {
        return getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false; 
        recognition.lang = 'pt-BR';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            autoExpand(); 
            input.focus();
        };

        recognition.onstart = () => {
            microphoneBtn.style.color = 'red'; 
            microphoneBtn.innerHTML = '&#9737;'; // Ícone de escuta
            input.placeholder = 'Escutando... Fale agora.';
        };
        
        recognition.onend = () => {
            microphoneBtn.style.color = varToCSS('--color-highlight'); 
            microphoneBtn.innerHTML = '&#127908;'; // Ícone de microfone
            input.placeholder = 'Peça à Esperança';
        };
        
        recognition.onerror = (event) => {
            console.error('Erro de reconhecimento de fala:', event.error);
            microphoneBtn.style.color = varToCSS('--color-highlight');
            microphoneBtn.innerHTML = '&#127908;';
            input.placeholder = 'Peça à Esperança';
            
            if (event.error === 'not-allowed') {
                 alert("Acesso ao microfone negado. Verifique as permissões do seu navegador.");
            }
        };

        // Evento de clique para iniciar/parar o reconhecimento
        microphoneBtn.addEventListener('click', () => {
            try {
                if (input.disabled) return; 
                
                if (recognition.recognizing) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            } catch (e) {
                 console.error("Não foi possível iniciar o reconhecimento de fala.", e);
            }
        });

    } else {
        // Se o navegador não suportar, esconde o microfone e ajusta o padding
        microphoneBtn.style.display = 'none';
        input.style.paddingLeft = '20px'; 
    }


    // --- Ativar o envio por Enter ---
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { 
            e.preventDefault(); 
            enviarMensagem();
        }
    });

    // --- Ativar o envio por Clique ---
    enviarBtn.addEventListener('click', enviarMensagem);
});