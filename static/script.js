// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('pergunta-input');
    const enviarBtn = document.getElementById('enviar-btn');
    const chatBox = document.getElementById('chat-box');

    // Função para rolar para a mensagem mais recente
    function rolarParaBaixo() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Função para adicionar uma nova bolha de mensagem ao chat
    function adicionarMensagem(texto, remetente) {
        const div = document.createElement('div');
        div.className = `mensagem ${remetente}`;
        
        // Substituir \n por <br> para quebras de linha corretas no HTML
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
            return; // Não envia mensagens vazias
        }

        // 1. Exibe a mensagem do usuário imediatamente
        adicionarMensagem(pergunta, 'usuario');
        input.value = ''; // Limpa o input
        input.disabled = true;
        enviarBtn.disabled = true;

        // 2. Adiciona um indicador visual de carregamento da IA
        const loadingDiv = adicionarMensagem('Digitando...', 'ia');

        try {
            // 3. Envia a requisição para o endpoint /api/chat
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pergunta: pergunta })
            });

            // 4. Verifica se a resposta foi bem-sucedida (código 200-299)
            if (!response.ok) {
                // Se o status for 500 ou 400, lança um erro
                const errorData = await response.json().catch(() => ({ erro: 'Erro de comunicação desconhecido.' }));
                throw new Error(errorData.erro || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();

            // 5. Remove o indicador de carregamento
            chatBox.removeChild(loadingDiv);

            // 6. Exibe a resposta da IA
            adicionarMensagem(data.resposta, 'ia');

        } catch (error) {
            // 5. Remove o indicador de carregamento e mostra a mensagem de erro
            chatBox.removeChild(loadingDiv);
            console.error('Erro ao enviar mensagem:', error);
            
            let erroDisplay = error.message;
            if (erroDisplay.includes('Erro HTTP: 500')) {
                erroDisplay = "Erro do Servidor Interno. O backend pode ter caído. Tente recarregar a página.";
            } else if (erroDisplay.includes('Failed to fetch')) {
                erroDisplay = "Erro de conexão: Não foi possível alcançar o servidor. Verifique o status da sua conexão ou se o Render está ativando o serviço.";
            }

            adicionarMensagem(`Erro: ${erroDisplay}`, 'ia');
        } finally {
            // 7. Reabilita o input e o botão
            input.disabled = false;
            enviarBtn.disabled = false;
            input.focus();
            rolarParaBaixo();
        }
    }

    // --- Ativar o envio por Enter ---
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { // Se for 'Enter' e não for 'Shift + Enter'
            e.preventDefault(); // Impede a quebra de linha padrão do Enter
            enviarMensagem();
        }
    });

    // --- Ativar o envio por Clique ---
    enviarBtn.addEventListener('click', enviarMensagem);
    
    // Rola para o final da conversa ao carregar (para ver a saudação inicial)
    rolarParaBaixo();
});