import serial
import json
import requests
import time
import sys


portaSerial = 'COM7'       
taxaTransmissao  = 9600
urlApi   = 'http://localhost:5000/leituras'
maximoTentativasConexao = 5
tempoEsperaReconexaoSegundos     = 3  


def enviarParaApi(dadosSensor: dict) -> bool:
    try:
        respostaApi = requests.post(urlApi, json=dadosSensor, timeout=5)
        if respostaApi.status_code == 201:
            return True
        print(f'[AVISO] API retornou {respostaApi.status_code}: {respostaApi.text}')
        return False
    except requests.exceptions.ConnectionError:
        print('Não foi possível conectar à API')
        return False
    except requests.exceptions.Timeout:
        print('Timeout ao tentar enviar para a API')
        return False


def processarLinhaSerial(linhaBruta: str):
    if not linhaBruta:
        return
    try:
        dadosAnalisados = json.loads(linhaBruta)
        sucessoEnvio = enviarParaApi(dadosAnalisados)
        if sucessoEnvio:
            pass # Pode adicionar log de sucesso aqui
    except json.JSONDecodeError:
        print(f'Erro: {linhaBruta}')


# Loop principal

def lerDaSerial():
    contagemTentativasAtual = 0

    while contagemTentativasAtual < maximoTentativasConexao:
        try:
            with serial.Serial(portaSerial, taxaTransmissao, timeout=2) as conexaoSerialAtiva:
                print(f'Conectado')
                contagemTentativasAtual = 0
                while True:
                    try:
                        linhaBytesBrutos = conexaoSerialAtiva.readline()
                        stringLinhaDecodificada = linhaBytesBrutos.decode('utf-8', errors='ignore').strip()
                        processarLinhaSerial(stringLinhaDecodificada)
                        time.sleep(0.1)
                    except UnicodeDecodeError:
                        print('Erro ao decodificar linha')

        except serial.SerialException as detalhesErroSerial:
            contagemTentativasAtual += 1
            print(f'Falha na serial: {detalhesErroSerial}')
            time.sleep(tempoEsperaReconexaoSegundos)

        except KeyboardInterrupt:
            sys.exit(0)

    sys.exit(1)


if __name__ == '__main__':
    print()
    lerDaSerial()
