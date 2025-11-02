// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // 1. Pega os dados que o Python "escondeu" no HTML
    const chartDataElement = document.getElementById('chart-data');
    if (!chartDataElement) {
        console.error("Elemento 'chart-data' não encontrado. O gráfico não pode ser inicializado.");
        return;
    }
    const data = JSON.parse(chartDataElement.textContent);

    const total = data.total;
    const disponivel = data.disponivel;
    const manutencao = data.manutencao;
    const indisponivel = data.indisponivel;

    if (total === 0) {
        // Se não há máquinas, mostra um gráfico vazio ou um aviso
        console.warn("Nenhuma máquina encontrada. Gráfico de distribuição vazio.");
        return;
    }

    // 2. Seleciona os elementos SVG do seu HTML
    const pieChart = document.querySelector('.pie-chart');
    const circleDisponivel = pieChart.querySelector('circle[stroke="#4CAF50"]'); // Verde
    const circleManutencao = pieChart.querySelector('circle[stroke="#2196F3"]'); // Azul
    const circleIndisponivel = pieChart.querySelector('circle[stroke="#F44336"]'); // Vermelho
    const textElement = pieChart.querySelector('text'); // O texto "Máquinas"

    // Circunferência de um círculo de raio 90 (2 * PI * R)
    const circumference = 2 * Math.PI * 90; // Aproximadamente 565.48

    // 3. Calcula as porcentagens e comprimentos das fatias
    const percDisponivel = (disponivel / total);
    const percManutencao = (manutencao / total);
    const percIndisponivel = (indisponivel / total);

    const lenDisponivel = circumference * percDisponivel;
    const lenManutencao = circumference * percManutencao;
    const lenIndisponivel = circumference * percIndisponivel;

    // 4. Calcula os offsets para empilhar as fatias corretamente
    // A primeira fatia começa em 0 offset
    // A segunda começa onde a primeira termina
    // A terceira começa onde a segunda termina
    const offsetManutencao = lenDisponivel; // Onde a "disponível" termina
    const offsetIndisponivel = lenDisponivel + lenManutencao; // Onde a "manutencao" termina

    // 5. Aplica os valores calculados aos elementos SVG
    if (circleDisponivel) {
        circleDisponivel.setAttribute('stroke-dasharray', `${lenDisponivel} ${circumference - lenDisponivel}`);
        circleDisponivel.setAttribute('stroke-dashoffset', 0); // Sempre começa em 0
    }
    if (circleManutencao) {
        circleManutencao.setAttribute('stroke-dasharray', `${lenManutencao} ${circumference - lenManutencao}`);
        circleManutencao.setAttribute('stroke-dashoffset', -offsetManutencao); // Offset é negativo
    }
    if (circleIndisponivel) {
        circleIndisponivel.setAttribute('stroke-dasharray', `${lenIndisponivel} ${circumference - lenIndisponivel}`);
        circleIndisponivel.setAttribute('stroke-dashoffset', -offsetIndisponivel); // Offset é negativo
    }

    // 6. Atualiza o texto central com o total de máquinas
    if (textElement) {
        textElement.textContent = `${total} Máquinas`; // Ou você pode usar 'Total' se quiser
    }

    console.log("Gráfico de distribuição atualizado com sucesso!");
});