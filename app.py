from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Rota para a página principal (IDE)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de ATIVIDADES
@app.route('/atividades')
def atividades():
    return render_template('atividades.html')

# Rota para a página de MATERIAIS
@app.route('/materiais')
def materiais():
    return render_template('materiais.html')

# Rota para EXECUTAR o código
@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    output_message = f"Simulação local bem-sucedida!\n---------------------------------\nCódigo recebido:\n\n{code}"
    return jsonify({"output": output_message})

if __name__ == '__main__':
    app.run(debug=True, port=5000)