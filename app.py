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
def execute_potigol_code(code_string, user_input_string=""):
    """
    Recebe código e uma string de entrada, executa no Docker
    e retorna a saída.
    """
    temp_filename = f"temp_script_{os.urandom(8).hex()}.poti"
    script_path = os.path.join(os.getcwd(), temp_filename)

    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(code_string)

        # ATUALIZAÇÃO: Adicionamos a flag '-i' para modo interativo
        command = [
            "sudo", "docker", "run", "-i", "--rm",
            "--network=none",
            "-v", f"{script_path}:/app/script.poti:ro",
            "potigol-runner",
            "script.poti"
        ]
        
        # ATUALIZAÇÃO: Passamos a entrada do usuário para o 'input' do processo
        result = subprocess.run(
            command, 
            input=user_input_string, # AQUI ESTÁ A MÁGICA
            capture_output=True, 
            text=True, 
            timeout=10,
            encoding='utf-8'
        )
        
        return result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        return "Erro: O código demorou muito para executar (limite de 10 segundos)."
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
    user_input = data.get('user_input', '') # Pega a entrada do usuário
    output = execute_potigol_code(code, user_input) # Passa a entrada para a função
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