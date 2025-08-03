import subprocess
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')

    # Cria um arquivo temporário para o código do aluno
    script_path = os.path.join(os.getcwd(), "temp_script.poti")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(code)

    try:
        # Comando para rodar o Potigol dentro do container Docker
        command = [
            "sudo", "docker", "run", "--rm",
            "--network=none",
            "-v", f"{script_path}:/app/temp_script.poti:ro",
            "potigol-runner",
            "temp_script.poti"
        ]

        # Executa o comando com um timeout de 10 segundos
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=60,
            encoding='utf-8'
        )

        output = result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        output = "Erro: O código demorou muito para executar (limite de 10 segundos)."
    except Exception as e:
        output = f"Erro inesperado no servidor: {str(e)}"

    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
