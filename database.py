import sqlite3
import os

caminhoBanco = os.path.join(os.path.dirname(__file__), 'dados.db')
caminhoEsquema = os.path.join(os.path.dirname(__file__), 'schema.sql')


def obterConexaoBanco():
    conexao = sqlite3.connect(caminhoBanco, timeout=10)
    conexao.execute('PRAGMA journal_mode=WAL')
    conexao.execute('PRAGMA busy_timeout=5000')
    conexao.row_factory = sqlite3.Row
    return conexao


def initDb():
    with open(caminhoEsquema, 'r') as arquivo:
        esquema = arquivo.read()
    conexao = obterConexaoBanco()
    conexao.executescript(esquema)
    conexao.commit()
    conexao.close()


def inserirLeitura(temperatura, umidade, pressao=None, localizacao='Lab'):
    conexao = obterConexaoBanco()
    cursor = conexao.execute(
        'INSERT INTO leituras (temperatura, umidade, pressao, localizacao) VALUES (?, ?, ?, ?)',
        (temperatura, umidade, pressao, localizacao)
    )
    conexao.commit()
    novoId = cursor.lastrowid
    conexao.close()
    return novoId


def listarLeituras(limite=50, offset=0):
    conexao = obterConexaoBanco()
    if limite is None:
        linhas = conexao.execute(
            'SELECT * FROM leituras ORDER BY timestamp DESC'
        ).fetchall()
    else:
        linhas = conexao.execute(
            'SELECT * FROM leituras ORDER BY timestamp DESC LIMIT ? OFFSET ?',
            (limite, offset)
        ).fetchall()
    total = conexao.execute('SELECT COUNT(*) FROM leituras').fetchone()[0]
    conexao.close()
    return linhas, total


def buscarLeitura(id):
    conexao = obterConexaoBanco()
    linha = conexao.execute('SELECT * FROM leituras WHERE id = ?', (id,)).fetchone()
    conexao.close()
    return linha


def atualizarLeitura(id, dados):
    campos = []
    valores = []
    for campoPesquisa in ('temperatura', 'umidade', 'pressao', 'localizacao'):
        if campoPesquisa in dados:
            campos.append(f'{campoPesquisa} = ?')
            valores.append(dados[campoPesquisa])
    if not campos:
        return False
    valores.append(id)
    conexao = obterConexaoBanco()
    conexao.execute(
        f'UPDATE leituras SET {", ".join(campos)} WHERE id = ?',
        valores
    )
    conexao.commit()
    conexao.close()
    return True


def deletarLeitura(id):
    conexao = obterConexaoBanco()
    conexao.execute('DELETE FROM leituras WHERE id = ?', (id,))
    conexao.commit()
    conexao.close()


def getEstatisticas():
    conexao = obterConexaoBanco()
    estatisticasAtuais = conexao.execute('''
        SELECT
            ROUND(AVG(temperatura), 2) as temp_media,
            ROUND(MIN(temperatura), 2) as temp_min,
            ROUND(MAX(temperatura), 2) as temp_max,
            ROUND(AVG(umidade), 2)     as umid_media,
            ROUND(MIN(umidade), 2)     as umid_min,
            ROUND(MAX(umidade), 2)     as umid_max,
            COUNT(*)                   as total
        FROM leituras
    ''').fetchone()
    conexao.close()
    return estatisticasAtuais
