import subprocess
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Respostas Esperadas para as Atividades ---
# A chave (ex: 'atividade-1') corresponde ao ID do card no HTML.
# O '\n' é importante porque a função 'escreva' do Potigol adiciona uma nova linha.
expected_outputs = {
    "atividade-1": "Potigol é legal!\n",
    "atividade-2": "Douglas\n30\n" # Exemplo: nome em uma linha, idade na outra
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
def execute_potigol_code(code_string, user_input_string=""):
    """
    Recebe código e uma string de entrada, executa no Docker
    e retorna a saída.
    """
    temp_filename = f"temp_script_{os.urandom(8).hex()}.poti"
    # Garante que o caminho seja absoluto para o diretório de trabalho atual
    script_path = os.path.join(os.getcwd(), temp_filename)

    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(code_string)

        command = [
            "sudo", "docker", "run", "-i", "--rm",
            "--network=none",
            "-v", f"{script_path}:/app/script.poti:ro",
            "potigol-runner",
            "script.poti"
        ]
        
        # Passamos a entrada do usuário para o 'input' do processo
        result = subprocess.run(
            command, 
            input=user_input_string,
            capture_output=True, 
            text=True, 
            timeout=15, # Timeout ajustado para 15 segundos
            encoding='utf-8'
        )
        
        return result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        return "Erro: O código demorou muito para executar (limite de 15 segundos)."
    except Exception as e:
        return f"Erro inesperado no servidor: {str(e)}"
    
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

# --- Rotas de Funcionalidade ---
@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    user_input = data.get('user_input', '')
    output = execute_potigol_code(code, user_input)
    return jsonify({"output": output})

@app.route('/verify', methods=['POST'])
def verify_answer():
    data = request.json
    code = data.get('code', '')
    activity_id = data.get('activity_id', '')
    user_input = data.get('user_input', '') # Pega a entrada do usuário do modal

    if not activity_id or activity_id not in expected_outputs:
        return jsonify({"correct": False, "output": "ID da atividade inválido."})

    # CORREÇÃO: Passa o user_input para a função de execução
    actual_output = execute_potigol_code(code, user_input)
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

# O bloco if __name__ == '__main__': foi removido, pois não é utilizado em produção com Gunicorn.