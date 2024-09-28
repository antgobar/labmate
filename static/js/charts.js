async function getMeasurementData(endpoint) {
    const protocol = window.location.protocol;
    const host = window.location.host;
    const url = `${protocol}//${host}/${endpoint}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errorDetails = await response.text();
            throw new Error(`Network response was not ok: ${response.status} - ${errorDetails}`);
        }
        measurementData = await response.json();
        updateDropdowns();
        initialisePlot();
        updateChart();
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}

function updateDropdowns() {
    const xDropdown = document.getElementById('xAxis');
    const yDropdown = document.getElementById('yAxis');

    xDropdown.innerHTML = '';
    yDropdown.innerHTML = '';

    measurementData.variables.forEach(varItem => {
        const optionX = document.createElement('option');
        optionX.value = varItem.name;
        optionX.textContent = `${varItem.name} (${varItem.unit})`;
        xDropdown.appendChild(optionX);

        const optionY = document.createElement('option');
        optionY.value = varItem.name;
        optionY.textContent = `${varItem.name} (${varItem.unit})`;
        yDropdown.appendChild(optionY);
    });

    xDropdown.addEventListener('change', updateChart);
    yDropdown.addEventListener('change', updateChart);
}

function updateChart() {
    const xAxisValue = document.getElementById('xAxis').value;
    const yAxisValue = document.getElementById('yAxis').value;

    if (xAxisValue && yAxisValue) {
        transformedData = measurementData.data_points.map(dataPoint => {
            return {
                x: dataPoint[xAxisValue],
                y: dataPoint[yAxisValue]
            };
        });

        currentChart.data.datasets[0].data = transformedData;
        currentChart.data.datasets[0].label = `${xAxisValue} vs ${yAxisValue}`;
        currentChart.options.scales.x.title.text = xAxisValue;
        currentChart.options.scales.y.title.text = yAxisValue;

        currentChart.update();
    }
}

function initialisePlot() {
    if (currentChart) {
        currentChart.destroy();
    }

    const xAxisName = document.getElementById('xAxis').value;
    const yAxisName = document.getElementById('yAxis').value;

    const config = {
        type: 'scatter',
        data: {
            datasets: [{
                label: `${xAxisName} vs ${yAxisName}`,
                data: transformedData,
            }],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: xAxisName,
                    },
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: yAxisName,
                    },
                },
            },
            elements: {
                point: {
                    radius: 8,
                    hoverRadius: 10,
                },
            },
        },
    };
    const ctx = document.getElementById(
        'chartSpace').getContext('2d');

    var newChart = new Chart(ctx, config);
    currentChart = newChart
}

function onChartLineTypeChange() {
    const chartType = document.querySelector('input[name="chartType"]:checked').value;

    if (chartType === 'scatter') {
        currentChart.config.type = 'scatter';
        currentChart.config.options.elements.point.radius = 8; // Show points
    } else if (chartType === 'line') {
        currentChart.config.type = 'line';
        currentChart.config.options.elements.point.radius = 0; // Hide points
    } else if (chartType === 'lineWithPoints') {
        currentChart.config.type = 'line';
        currentChart.config.options.elements.point.radius = 8; // Show points
    }

    currentChart.update();
}
