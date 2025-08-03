import subprocess
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Respostas Esperadas para as Atividades ---
# A chave (ex: 'atividade-1') corresponde ao ID do card no HTML.
# O '\n' é importante porque a função 'escreva' do Potigol adiciona uma nova linha.
expected_outputs = {
    "atividade-1": "Potigol é legal!\n",
    "atividade-2": "fulado\n30\n",
    "atividade-3": "Qual é o seu nome?\nSeja bem-vinda, Ana!\n", 
    "atividade-4": "Digite seu nome:\nDigite sua idade:\nO usuário Carlos tem 32 anos.\n", 
    "atividade-5": "Nome:\nCidade:\nProfissão:\n--- Cadastro Realizado ---\nNome: Mariana\nCidade: Salvador\nProfissão: Engenheira\n", 
    "atividade-6": "Qual é a sua comida favorita?\nPizza é uma ótima escolha para hoje!\n", 
    "atividade-7": "Em que ano você nasceu?\nQual é o ano atual?\nVocê tem ou fará 30 anos em 2025.\nDaqui a 10 anos, você terá 40 anos!\n", 
    "atividade-8": "Digite a sua altura em metros (use ponto para decimais):\nSua altura em centímetros é: 175.0 cm.\n", 
    "atividade-9": "Olá! Qual o seu nome?\nBem-vindo, Rafael! De qual cidade você é?\nE qual a temperatura em graus Celsius aí em Recife agora?\nUau, Rafael! Parece que está um dia quente em Recife.\n" 
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