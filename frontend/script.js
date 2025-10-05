const apiBase = "http://127.0.0.1:8000"; // <-- mets l'URL de ton API FastAPI ici

document.getElementById("regressionBtn").addEventListener("click", () => {
  sendRequest("regression");
});

document.getElementById("classificationBtn").addEventListener("click", () => {
  sendRequest("classification");
});

async function sendRequest(type) {
  const day = parseInt(document.getElementById("day").value);
  const month = parseInt(document.getElementById("month").value);
  const year = parseInt(document.getElementById("year").value);

  if (!day || !month || !year) {
    showResult("❌ Veuillez remplir tous les champs.", "error");
    return;
  }

  const features = {
    dayofyear: day + (month - 1) * 30, // approximation simple
    month: month,
    year: year,
    dayofweek: new Date(year, month - 1, day).getDay(),
    T2M_lag1: 28.0,
    T2M_lag3: 27.5,
    RH2M_lag1: 75.0,
    RH2M_lag3: 77.0,
    PS_lag1: 101.2,
    PS_lag3: 101.4,
    WS2M_lag1: 2.5,
    WS2M_lag3: 2.7,
    PRECTOTCORR_lag1: 0.0,
    PRECTOTCORR_lag3: 5.0,
  };

  try {
    const response = await fetch(`${apiBase}/predict/${type}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(features),
    });

    if (!response.ok) {
      throw new Error("Erreur API");
    }

    const data = await response.json();
    displayOutput(type, data);
  } catch (error) {
    showResult("❌ Erreur de connexion à l’API.", "error");
  }
}

function displayOutput(type, data) {
  const output = document.getElementById("output");
  output.innerHTML = "";

  if (type === "regression") {
    output.innerHTML += `<div class="card">🌡️ Température : ${data.Temperature_C} °C</div>`;
    output.innerHTML += `<div class="card">💧 Humidité : ${data.Humidity_percent} %</div>`;
    output.innerHTML += `<div class="card">📊 Pression : ${data.Pressure_kPa} kPa</div>`;
    output.innerHTML += `<div class="card">🌬️ Vent : ${data.Wind_m_s} m/s</div>`;
  } else if (type === "classification") {
    const rain = data.Rain_Prediction;
    const prob = data.Probability * 100;
    const cssClass = rain.includes("Oui") ? "success" : "warning";
    output.innerHTML = `<div class="card ${cssClass}">${rain} (Probabilité : ${prob.toFixed(
      1
    )} %)</div>`;
  }
}

function showResult(message, cssClass) {
  const output = document.getElementById("output");
  output.innerHTML = `<div class="card ${cssClass}">${message}</div>`;
}
