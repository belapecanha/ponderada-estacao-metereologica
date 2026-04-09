from flask import Flask, request, jsonify, render_template, redirect, url_for
from database import initDb, inserirLeitura, listarLeituras, buscarLeitura, atualizarLeitura, deletarLeitura, getEstatisticas

app = Flask(__name__)

# Inicializa o banco ao subir o servidor
with app.app_context():
    initDb()


# Home

@app.route('/')
def index():
    leituras, _ = listarLeituras(limite=10)
    return render_template('index.html', leituras=leituras)


# Histórico

@app.route('/leituras')
def listar():
    formatoRequisicao = request.args.get('formato')

    leiturasRestantes, _ = listarLeituras(limite=None)

    if formatoRequisicao == 'json':
        return jsonify([dict(itemLeitura) for itemLeitura in leiturasRestantes])

    return render_template(
        'historico.html',
        leituras=leiturasRestantes
    )


# Criar leitura

@app.route('/leituras', methods=['POST'])
def criar():
    dadosRecebidos = request.get_json()
    if not dadosRecebidos:
        return jsonify({'erro': 'JSON inválido'}), 400

    temperaturaAtual = dadosRecebidos.get('temperatura')
    umidadeAtual = dadosRecebidos.get('umidade')

    if temperaturaAtual is None or umidadeAtual is None:
        return jsonify({'erro': 'temperatura e umidade são obrigatórios'}), 400

    try:
        temperaturaAtual = float(temperaturaAtual)
        umidadeAtual = float(umidadeAtual)
    except (ValueError, TypeError):
        return jsonify({'erro': 'Valores devem ser numéricos'}), 400

    pressaoAtual = dadosRecebidos.get('pressao')
    localizacaoAtual = dadosRecebidos.get('localizacao', 'Lab')

    novoId = inserirLeitura(temperaturaAtual, umidadeAtual, pressaoAtual, localizacaoAtual)
    return jsonify({'id': novoId, 'status': 'criado'}), 201


# Detalhe de uma leitura

@app.route('/leituras/<int:id>')
def detalhe(id):
    leituraEncontrada = buscarLeitura(id)
    if leituraEncontrada is None:
        return jsonify({'erro': 'Leitura não encontrada'}), 404

    formatoRequisicao = request.args.get('formato')
    if formatoRequisicao == 'json':
        return jsonify(dict(leituraEncontrada))

    return render_template('detalhe.html', leitura=leituraEncontrada)


# Atualizar leitura 

@app.route('/leituras/<int:id>', methods=['PUT'])
def atualizar(id):
    leituraEncontrada = buscarLeitura(id)
    if leituraEncontrada is None:
        return jsonify({'erro': 'Leitura não encontrada'}), 404

    dadosAtualizar = request.get_json() or request.form.to_dict()
    # converte strings numéricas vindas do formulário
    for campoRecebido in ('temperatura', 'umidade', 'pressao'):
        if campoRecebido in dadosAtualizar and dadosAtualizar[campoRecebido] != '':
            try:
                dadosAtualizar[campoRecebido] = float(dadosAtualizar[campoRecebido])
            except ValueError:
                return jsonify({'erro': f'Valor inválido para {campoRecebido}'}), 400

    atualizacaoOk = atualizarLeitura(id, dadosAtualizar)
    if not atualizacaoOk:
        return jsonify({'erro': 'Nenhum campo válido para atualizar'}), 400

    return jsonify({'status': 'atualizado'})

@app.route('/leituras/<int:id>/editar', methods=['GET'])
def editar_form(id):
    leituraEncontrada = buscarLeitura(id)
    if leituraEncontrada is None:
        return 'Leitura não encontrada', 404
    return render_template('editar.html', leitura=leituraEncontrada)


@app.route('/leituras/<int:id>/editar', methods=['POST'])
def editar_submit(id):
    dadosFormulario = {
        'temperatura': request.form.get('temperatura'),
        'umidade': request.form.get('umidade'),
        'pressao': request.form.get('pressao') or None,
        'localizacao': request.form.get('localizacao', 'Lab'),
    }
    for campoNumerico in ('temperatura', 'umidade'):
        try:
            dadosFormulario[campoNumerico] = float(dadosFormulario[campoNumerico])
        except (ValueError, TypeError):
            return 'Valor inválido', 400
    if dadosFormulario['pressao']:
        try:
            dadosFormulario['pressao'] = float(dadosFormulario['pressao'])
        except ValueError:
            dadosFormulario['pressao'] = None

    atualizarLeitura(id, dadosFormulario)
    return redirect(url_for('listar'))


# Deletar leitura 

@app.route('/leituras/<int:id>', methods=['DELETE'])
def deletar(id):
    leituraEncontrada = buscarLeitura(id)
    if leituraEncontrada is None:
        return jsonify({'erro': 'Leitura não encontrada'}), 404
    deletarLeitura(id)
    return jsonify({'status': 'deletado'})


@app.route('/leituras/<int:id>/deletar', methods=['POST'])
def deletar_form(id):
    deletarLeitura(id)
    return redirect(url_for('listar'))


#  Estatísticas 

@app.route('/api/estatisticas')
def estatisticas():
    dadosEstatisticos = getEstatisticas()
    return jsonify(dict(dadosEstatisticos))


# Gráfico

@app.route('/api/leituras/recentes')
def leituras_recentes():
    numeroRegistros = int(request.args.get('n', 30))
    listaLeituras, _ = listarLeituras(limite=numeroRegistros)
    return jsonify([dict(leituraItem) for leituraItem in reversed(list(listaLeituras))])


if __name__ == '__main__':
    app.run(debug=True)
