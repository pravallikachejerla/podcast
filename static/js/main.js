function fetchChartData(url, chartId, label, color) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById(chartId).getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.date),
                    datasets: [{
                        label: label,
                        data: data.map(d => d.daily_listeners || d.predicted_listeners),
                        borderColor: color,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
}
