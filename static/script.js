function showError(msg) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = msg;
}

function clearError() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = '';
}

const input = document.getElementById('location-input');
const suggestions = document.getElementById('suggestions');
const weatherResult = document.getElementById('weather-result');
const form = document.getElementById('search-form');

window.onload = () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((pos) => {
            const { latitude, longitude } = pos.coords;
            fetchWeather(latitude, longitude, 'current');
        });
    }
};

input.addEventListener('input', () => {
    const val = input.value.trim();
    if (val.length < 2) {
        suggestions.innerHTML = '';
        return;
    }
    fetch(`/search_location?q=${encodeURIComponent(val)}`)
        .then(res => res.json())
        .then(data => {
            suggestions.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.name}${item.state ? ', ' + item.state : ''}, ${item.country}`;
                li.addEventListener('click', () => {
                    input.value = li.textContent;
                    suggestions.innerHTML = '';
                    fetchWeather(item.lat, item.lon, 'search');
                });
                suggestions.appendChild(li);
            });
        });
});

form.addEventListener('submit', (e) => {
    e.preventDefault();
    const val = input.value.trim();
    if (!val) return;
    fetch(`/search_location?q=${encodeURIComponent(val)}`)
        .then(res => res.json())
        .then(data => {
            if (data.length > 0) {
                const item = data[0];
                fetchWeather(item.lat, item.lon, 'search');
                suggestions.innerHTML = '';
                clearError();
            } else {
            showError(`❌ Location not found for "${val}"`);
            }
        });
});

let chartInstances = {};

function fetchWeather(lat, lon, type) {
    fetch(`/get_weather?lat=${lat}&lon=${lon}`)
        .then(res => res.json())
        .then(current => {
            fetch(`/get_forecast?lat=${lat}&lon=${lon}`)
                .then(res => res.json())
                .then(forecast => {
                    fetch(`/get_hourly?lat=${lat}&lon=${lon}`)
                        .then(res => res.json())
                        .then(hourly => {
                            displayWeather(current, forecast, hourly, type);
                        });
            });
        });
}

function loadAdditionalData(location) {
    if (!location) return;

    fetch('/api/youtube_videos?location=' + encodeURIComponent(location))
        .then(res => res.json())
        .then(videos => {
            const container = document.getElementById('youtube-videos');
            container.innerHTML = '';
            videos.forEach(video => {
                const div = document.createElement('div');
                div.style.marginBottom = '10px';
                div.innerHTML = `
                    <a href="https://www.youtube.com/watch?v=${video.videoId}" target="_blank" rel="noopener noreferrer">
                        <img src="${video.thumbnail}" alt="${video.title}" />
                        <p>${video.title}</p>
                    </a>
                `;
                container.appendChild(div);
            });
        });
    }


function displayWeather(current, forecast, hourly, type) {
    const existing = document.getElementById(`${type}-weather`);
    if (existing) existing.remove();

    const wrapper = document.createElement('div');
    wrapper.id = `${type}-weather`;

    const iconUrl = `https://openweathermap.org/img/wn/${current.weather[0].icon}@2x.png`;
    const weatherIcon = `<img src="${iconUrl}" alt="icon" style="width:48px; height:48px;">`;

    const infoDiv = document.createElement('div');
    infoDiv.className = 'weather-info';
    infoDiv.innerHTML = `
        <h2>${type === 'current' ? '🌍 Your Location' : '📍 Searched Location'}: ${current.name}</h2>
        ${weatherIcon}
        <p><strong>Clouds:</strong> ${current.weather[0].description}</p>
        <p>Temp: ${current.main.temp} °C</p>
        <p>Humidity: ${current.main.humidity}%</p>
        <p>Wind Speed: ${current.wind.speed} m/s</p>
        <h3>5-Day Forecast</h3>
        <ul>
            ${forecast.list
                .filter((_, i) => i % 8 === 0)
                .map(entry => {
                    const date = new Date(entry.dt * 1000).toLocaleDateString();
                    const icon = `https://openweathermap.org/img/wn/${entry.weather[0].icon}.png`;
                    return `<li><strong>${date}</strong> - <img src="${icon}" class="forecast-icon"> ${entry.weather[0].main}, Temp: ${entry.main.temp.toFixed(2)}°C</li>`;
                }).join('')}
        </ul>
    `;

    const chartDiv = document.createElement('div');
    chartDiv.className = 'chart-wrapper';
    const canvas = document.createElement('canvas');
    canvas.id = `chart-${type}`;
    chartDiv.appendChild(canvas);

    const section = document.createElement('div');
    section.className = 'weather-section';
    section.appendChild(infoDiv);
    section.appendChild(chartDiv);

    wrapper.appendChild(section);
    weatherResult.appendChild(wrapper);

    // draw chart
    const ctx = canvas.getContext('2d');
    const labels = hourly.list.map(item => new Date(item.dt * 1000).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}));
    const temps = hourly.list.map(item => item.main.temp);

    if (chartInstances[type]) chartInstances[type].destroy();

    chartInstances[type] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Hourly Temp (°C)',
                data: temps,
                borderColor: 'orange',
                backgroundColor: 'rgba(255,165,0,0.3)',
                fill: true,
                pointRadius: 3,
                tension: 0.3
            }]
        },
        options: {
        responsive: true,
        scales: {
            x: { title: { display: true, text: 'Time' } },
            y: { title: { display: true, text: 'Temperature (°C)' } }
            }
        }
    });
    loadAdditionalData(current.name)
}
