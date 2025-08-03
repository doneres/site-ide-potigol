// Este script é APENAS para a página principal (index.html)

// Inicializa o editor CodeMirror da página principal
const editor = CodeMirror.fromTextArea(document.getElementById("codeInput"), {
    lineNumbers: true,
    mode: 'text/x-csrc',
    theme: 'eclipse',
    lineWrapping: true,
    autofocus: true
});

// Adiciona a função ao botão "Executar"
document.getElementById('runButton').addEventListener('click', runCode);

async function runCode() {
    const code = editor.getValue();
    const userInput = document.getElementById('programInput').value;
    const outputElement = document.getElementById('output');
    
    outputElement.textContent = 'Executando...';

    try {
        const response = await fetch('/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code, user_input: userInput })
        });

        const result = await response.json();
        outputElement.textContent = result.output;
    } catch (error) {
        outputElement.textContent = 'Erro ao conectar com o servidor: ' + error.message;
    }
}