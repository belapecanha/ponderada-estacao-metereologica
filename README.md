# Sistema de Medição de Estação Meteorológica IoT


## Decisão de Arquitetura

A arquitetura que escolhi foi a sugerida no enunciado, usar o hardware físico diretamente.

- Sensor DHT11 conectado ao Arduino lê temperatura e umidade
- O Arduino envia os dados pela porta serial no formato JSON a cada 3 segundos
- Um processo Python separado (`serial_reader.py`) lê a serial e faz POST para a API
- A API Flask recebe, valida e persiste os dados no SQLite
- A interface web consome os endpoints e exibe as leituras em tempo real

---

## Hardware

### Componentes utilizados

- 1 Arduino Uno
- 1 Sensor DHT11 (temperatura e umidade)
- Resistor de 10 kΩ (pull-up)
- Cabos jumper
- Protoboard
- Cabo USB

### Circuito

| DHT11 | Arduino |
|-------|---------|
| VCC   | 5V      |
| GND   | GND     |
| DATA  | Pino Digital 4 (com um resistor de 10 kΩ para 5V) |

### Hardware montado

![Hardware - visão geral](/static/img/ex1.jpeg)

![Hardware - detalhe do sensor](/static/img/ex2.jpeg)

---

## Estrutura do Projeto

```
src/
├── app.py
├── database.py
├── serial_reader.py
├── schema.sql
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── historico.html
│   ├── editar.html
│   └── detalhe.html
├── arduino/
│   └── estacao.ino
└── README.md
```

---

## Instalação e Execução


### 1. Clonar o repositório

```bash
git clone <//>
cd src
```

### 2. Criar ambiente virtual e instalar dependências

```bash
python -m venv venv

venv\Scripts\activate

pip install flask pyserial requests
```

### 3. Gravar o sketch no Arduino

Abra o arquivo `arduino/estacao.ino` na Arduino IDE, selecione a porta correta e faça o upload.

### 4. Iniciar a API Flask

```bash
python app.py
```

O servidor sobe em `http://localhost:5000`.

### 5. Iniciar a leitura serial (em outro terminal)

```bash
python serial_reader.py
```

---

## Banco de Dados

Schema da tabela principal:

```sql
CREATE TABLE IF NOT EXISTS leituras (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    temperatura REAL NOT NULL,
    umidade     REAL NOT NULL,
    pressao     REAL,
    localizacao TEXT DEFAULT 'Lab',
    timestamp   DATETIME DEFAULT (datetime('now','localtime'))
);
```
---

## API REST — Rotas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Painel principal com as últimas 10 leituras |
| GET | `/leituras` | Histórico completo |
| GET | `/leituras?formato=json` | Histórico em JSON |
| POST | `/leituras` | Recebe nova leitura do Arduino |
| GET | `/leituras/<id>` | Detalhe de uma leitura |
| PUT | `/leituras/<id>` | Atualiza uma leitura |
| DELETE | `/leituras/<id>` | Remove uma leitura |
| GET | `/api/estatisticas` | Média, mínimo e máximo do período |
| GET | `/api/leituras/recentes?n=30` | Últimas N leituras |

### Exemplo de payload POST

```json
{
  "temperatura": 24.5,
  "umidade": 68.0,
  "localizacao": "Lab"
}
```

Resposta esperada:

```json
{
  "id": 42,
  "status": "criado"
}
```

---

## Interface Web

- **Painel (`/`)** — exibe as últimas 10 leituras com temperatura, umidade e timestamp
- **Histórico (`/leituras`)** — tabela com todas as leituras, com opção de excluir cada linha
- **Edição (`/leituras/<id>/editar`)** — formulário pré-preenchido para corrigir valores de uma leitura
- **Detalhe (`/leituras/<id>`)** — visualização de uma leitura específica
- **Gráfico** — gráfico de variação temporal de temperatura e umidade usando Chart.js, atualizado via `/api/leituras/recentes`

---

## Código Arduino

O sketch envia os dados a cada 3 segundos no formato JSON pela porta serial 9600:

```cpp
#include "DHT.h"

#define DHTPIN  4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  delay(2000);
}

void loop() {
  float temp = dht.readTemperature();
  float umid = dht.readHumidity();

  if (!isnan(temp) && !isnan(umid)) {
    Serial.print("{\"temperatura\": ");
    Serial.print(temp);
    Serial.print(", \"umidade\": ");
    Serial.print(umid);
    Serial.println("}");
  }

  delay(3000);
}
```

---

