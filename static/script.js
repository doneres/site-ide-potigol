const editor = CodeMirror.fromTextArea(document.getElementById("codeInput"), {
    lineNumbers: true,
    mode: 'text/x-csrc',
    theme: 'default', // temas: https://codemirror.net/5/demo/theme.html#default
    lineWrapping: true,
    autofocus: true
});

// Adiciona um listener de evento para o botão
document.getElementById('runButton').addEventListener('click', runCode);

async function runCode() {
    const code = editor.getValue();
    const outputElement = document.getElementById('output');
    
    outputElement.textContent = 'Executando...';
    outputElement.style.color = '#f8f8f2';

    try {
        const response = await fetch('/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        });

        if (!response.ok) {
            throw new Error(`Erro do servidor: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        outputElement.textContent = result.output;
    } catch (error) {
        // Pega erros de conexão ou erros de servidor
        outputElement.textContent = 'Erro ao conectar com o servidor: ' + error.message;
        outputElement.style.color = '#ff6b6b';
    }
}