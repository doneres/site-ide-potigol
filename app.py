import subprocess
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Respostas Esperadas para as Atividades ---
# A chave (ex: 'atividade-1') corresponde ao ID do card no HTML.
# O '\n' é importante porque a função 'escreva' do Potigol adiciona uma nova linha.
expected_outputs = {
    "atividade-1": "Potigol é legal!\n",
    "atividade-2": "Seu Nome Completo\nSua Idade\n" # Exemplo, você ajustaria
}

# --- Rotas das Páginas ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/atividades')
def atividades():
    return render_template('atividades.html')

@app.route('/materiais')
def materiais():
    return render_template('materiais.html')

# --- Função Central de Execução de Código ---
def execute_potigol_code(code_string):
    """
    Recebe uma string de código, salva em um arquivo temporário,
    executa no Docker e retorna a saída.
    """
    # Cria um nome de arquivo temporário e único para evitar conflitos
    temp_filename = f"temp_script_{os.urandom(8).hex()}.poti"
    script_path = os.path.join(os.getcwd(), temp_filename)

    try:
        # Escreve o código do usuário no arquivo temporário
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(code_string)

        # Comando para rodar o Potigol dentro do container Docker
        command = [
            "sudo", "docker", "run", "--rm",
            "--network=none",
            "-v", f"{script_path}:/app/script.poti:ro",
            "potigol-runner",
            "script.poti"
        ]
        
        # Executa o comando com um timeout de 10 segundos
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=10,
            encoding='utf-8'
        )
        
        # Combina a saída padrão e a saída de erro para o usuário ver tudo
        return result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        return "Erro: O código demorou muito para executar (limite de 10 segundos)."
    except Exception as e:
        return f"Erro inesperado no servidor: {str(e)}"
    
    finally:
        # Garante que o arquivo temporário seja sempre removido, mesmo se der erro
        if os.path.exists(script_path):
            os.remove(script_path)

# --- Rotas de Funcionalidade ---
@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    output = execute_potigol_code(code)
    return jsonify({"output": output})

@app.route('/verify', methods=['POST'])
def verify_answer():
    data = request.json
    code = data.get('code', '')
    activity_id = data.get('activity_id', '')

    if not activity_id or activity_id not in expected_outputs:
        return jsonify({"correct": False, "output": "ID da atividade inválido."})

    actual_output = execute_potigol_code(code)
    expected_output = expected_outputs[activity_id]

    if actual_output.strip() == expected_output.strip():
        return jsonify({
            "correct": True, 
            "output": f"✅ Parabéns, resposta correta!\n\nSaída do seu programa:\n{actual_output}"
        })
    else:
        return jsonify({
            "correct": False, 
            "output": f"❌ Ops, resposta incorreta.\n\nSaída esperada:\n{expected_output}\nSua saída:\n{actual_output}"
        })

# Note que não há mais o bloco "if __name__ == '__main__':"
# Agora a execução é responsabilidade do Gunicorn e do Systemd.