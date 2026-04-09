async function carregarEstatisticas() {
  try {
    const respostaServidor = await fetch('/api/estatisticas');
    if (!respostaServidor.ok) return;
    const dadosEstatisticas = await respostaServidor.json();

    const elementoTemperatura = document.getElementById('val-temp');
    const elementoUmidade = document.getElementById('val-umid');
    const elementoTotalLeituras = document.getElementById('val-total');

    if (elementoTemperatura && dadosEstatisticas.temp_media !== null)  elementoTemperatura.textContent  = dadosEstatisticas.temp_media;
    if (elementoUmidade && dadosEstatisticas.umid_media !== null)  elementoUmidade.textContent  = dadosEstatisticas.umid_media;
    if (elementoTotalLeituras && dadosEstatisticas.total !== null)      elementoTotalLeituras.textContent = dadosEstatisticas.total;
  } catch (detalhesErro) {
    console.warn('Erro ao carregar estatísticas:', detalhesErro);
  }
}

async function carregarGrafico() {
  const canvasGrafico = document.getElementById('grafico');
  if (!canvasGrafico) return;

  try {
    const respostaServidor = await fetch('/api/leituras/recentes?n=30');
    if (!respostaServidor.ok) return;
    const leiturasRecentes = await respostaServidor.json();

    if (leiturasRecentes.length === 0) {
      canvasGrafico.parentElement.innerHTML = '<p class="empty-msg">Sem dados suficientes para o gráfico.</p>';
      return;
    }

    const rotulosTempo = leiturasRecentes.map(leitura => {
      const dataHora = new Date(leitura.timestamp);
      return dataHora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    });
    const valoresTemperatura = leiturasRecentes.map(leitura => leitura.temperatura);
    const valoresUmidade = leiturasRecentes.map(leitura => leitura.umidade);

    const contextoCanvas = canvasGrafico.getContext('2d');
    new Chart(contextoCanvas, {
      type: 'line',
      data: {
        labels: rotulosTempo,
        datasets: [
          {
            label: 'Temperatura (°C)',
            data: valoresTemperatura,
            borderColor: '#f9e2af',
            backgroundColor: 'rgba(249,226,175,0.08)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            fill: true,
          },
          {
            label: 'Umidade (%)',
            data: valoresUmidade,
            borderColor: '#89b4fa',
            backgroundColor: 'rgba(137,180,250,0.08)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            fill: true,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            labels: {
              color: '#cdd6f4',
              font: { family: "'JetBrains Mono', monospace", size: 11 }
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#6c7086',
              font: { family: "'JetBrains Mono', monospace", size: 10 },
              maxTicksLimit: 10,
            },
            grid: { color: 'rgba(255,255,255,0.04)' }
          },
          y: {
            ticks: {
              color: '#6c7086',
              font: { family: "'JetBrains Mono', monospace", size: 10 }
            },
            grid: { color: 'rgba(255,255,255,0.04)' }
          }
        }
      }
    });
  } catch (detalhesErro) {
    console.warn('Erro ao carregar gráfico:', detalhesErro);
  }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  carregarEstatisticas();
  carregarGrafico();
});
