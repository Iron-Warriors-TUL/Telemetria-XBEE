/* Wartości od których kolor temperatur robi się czerwony */
// const ENGINE_TEMP_LIMIT = 100;
// const OIL_TEMP_LIMIT = 110;

const ENGINE_TEMP_MIN_LIMIT = 90;
const ENGINE_TEMP_MAX_LIMIT = 120;

const OIL_TEMP_MIN_LIMIT = 90;
const OIL_TEMP_MAX_LIMIT = 120;

const EGT_MIN_LIMIT = 500;
const EGT_MAX_LIMIT = 1000;

const BATTERY_VOLTAGE_MIN_LIMIT = 14.0;
const BATTERY_VOLTAGE_MAX_LIMIT = 14.8;

function formatTime(sec) {
    const sign = sec < 0 ? "-" : "";
    sec = Math.abs(sec);
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${sign}${m}:${s.toString().padStart(2, "0")}`;
}

/* Sterowanie */

async function start() {
    await fetch("/api/config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            max_laps: max_laps.value,
            lap_target_time: lap_target_time.value
        })
    });

    await fetch("/api/control", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ action: "start" })
    });

    max_laps.disabled = true;
    lap_target_time.disabled = true;
    saveBtn.disabled = true;
}

async function reset() {
    await fetch("/api/control", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ action: "reset" })
    });

    clearUI();
    max_laps.disabled = false;
    lap_target_time.disabled = false;
    saveBtn.disabled = true;
}

async function lapInc() {
    await fetch("/api/lap", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ direction: "inc" })
    });
}

async function lapDec() {
    await fetch("/api/lap", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ direction: "dec" })
    });
}

/* Zapis danych */

async function save() {
    const res = await fetch("/api/save", { method: "POST" });
    const data = await res.json();

    if (data.file) {
        alert("Zapisano dane wyścigu:\n" + data.file);
        saveBtn.disabled = true;
    } else {
        alert("Brak danych do zapisania");
    }
}

/* User interface */

function clearUI() {
    lap_time.innerText = "--:--";
    lap_time_remaining.innerText = "--:--";
    race_time_remaining.innerText = "--:--";
    time_delta.innerText = "--";

    rpm.innerText = "0";
    speed.innerText = "0";

    engine_temp.innerText = "-";
    oil_temp.innerText = "-";
    intake_temp.innerText = "-";
    emission_temp.innerText = "-";

    lap_current.innerText = "-";
    lap_total.innerText = "-";
}

async function update() {
    const res = await fetch("/api/state");
    const data = await res.json();
    const battery_val = document.getElementById('battery_voltage');
    if (battery_val) {
        battery_val.innerText = data.battery_voltage.toFixed(1);
        if (data.battery_voltage < BATTERY_VOLTAGE_MIN_LIMIT) {
            battery_val.style.color = "red";
        } else if (data.battery_voltage >= BATTERY_VOLTAGE_MIN_LIMIT && data.battery_voltage <= BATTERY_VOLTAGE_MAX_LIMIT) {
            battery_val.style.color = "orange";
        } else {
            battery_val.style.color = "white";
        }
    }
    if (!data.running) {
        if (data.finished) {
            time_delta.innerText =
                (data.time_delta >= 0 ? "+" : "") + data.time_delta + "s";
            time_delta.style.color =
                data.time_delta >= 0 ? "#00ff66" : "#ff3333";

            lap_current.innerText = "KONIEC";
            lap_total.innerText = "WYŚCIGU";

            saveBtn.disabled = false;
        }
        return;
    }

    lap_time.innerText = formatTime(data.lap_time);
    lap_time_remaining.innerText = formatTime(data.lap_time_remaining);
    race_time_remaining.innerText = formatTime(data.race_time_remaining);

    time_delta.innerText =
        (data.time_delta >= 0 ? "+" : "") + data.time_delta + "s";
    time_delta.style.color =
        data.time_delta >= 0 ? "#00ff66" : "#ff3333";

    rpm.innerText = data.rpm;
    speed.innerText = data.speed;

    engine_temp.innerText = data.engine_temp;
    if (data.engine_temp < ENGINE_TEMP_MIN_LIMIT) {
        engine_temp.style.color = "white";
    } else if (data.engine_temp >= ENGINE_TEMP_MIN_LIMIT && data.engine_temp <= ENGINE_TEMP_MAX_LIMIT) {
        engine_temp.style.color = "green";
    } else {
        engine_temp.style.color = "red";
    }

    oil_temp.innerText = data.oil_temp;
    if (data.oil_temp < OIL_TEMP_MIN_LIMIT) {
        oil_temp.style.color = "white";
    } else if (data.oil_temp >= OIL_TEMP_MIN_LIMIT && data.oil_temp <= OIL_TEMP_MAX_LIMIT) {
        oil_temp.style.color = "green";
    } else {
        oil_temp.style.color = "red";
    }

    emission_temp.innerText = data.emission_temp;
    if (data.emission_temp < EGT_MIN_LIMIT) {
        emission_temp.style.color = "white";
    } else if (data.emission_temp >= EGT_MIN_LIMIT && data.emission_temp <= EGT_MAX_LIMIT) {
        emission_temp.style.color = "green";
    } else {
        emission_temp.style.color = "red";
    }

    intake_temp.innerText = data.intake_temp;
    lap_current.innerText = data.lap_current;
    lap_total.innerText = data.lap_total;
}

setInterval(update, 200);
