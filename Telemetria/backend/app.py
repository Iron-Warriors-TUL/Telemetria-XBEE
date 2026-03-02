from flask import Flask, jsonify, request, render_template
from telemetry.race_state import RaceState
from telemetry.data_source import XBeeTelemetrySource
from telemetry.race_logger import RaceLogger
from telemetry.mock_data import MockTelemetrySource
import time

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

data_source = XBeeTelemetrySource(port="/dev/serial0", baud=115200)
# data_source = MockTelemetrySource()
logger = RaceLogger()
race = RaceState(data_source, logger)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/config", methods=["POST"])
def config():
    data = request.json
    race.configure(
        lap_target_time=int(data["lap_target_time"]),
        max_laps=int(data["max_laps"])
    )
    return jsonify({"status": "configured"})


@app.route("/api/control", methods=["POST"])
def control():
    action = request.json.get("action")

    if action == "start":
        race.start()
    elif action == "reset":
        race.reset()

    return jsonify({"status": action})


@app.route("/api/lap", methods=["POST"])
def lap():
    direction = request.json.get("direction")
    if direction == "inc":
        race.change_lap(1)
    elif direction == "dec":
        race.change_lap(-1)
    return jsonify({"status": "ok"})


@app.route("/api/save", methods=["POST"])
def save():
    meta = request.json
    filename = logger.save_csv(meta)
    if filename:
        logger.generate_report_and_push(filename)
        return jsonify({"file": filename, "status": "saved_and_pushed"})

    return jsonify({"file": None, "status": "no_data"}), 400


@app.route("/api/state")
def state():
    s = race.get_state()

    sample = data_source.get_sample(0, 0)
    combined_data = {**sample, **s}

    # Jeśli wyścig trwa, wyślij dane do bolidu
    if s.get("running"):
        race_time = time.time() - race.start_time
        logger.log_data(
            race_time=race_time,
            lap_number=s.get('lap_current'),
            speed=combined_data.get('speed'),
            rpm=combined_data.get('rpm'),
            oil=combined_data.get('oil_temp'),
            clt=combined_data.get('engine_temp'),
            iat=combined_data.get('intake_temp'),
            egt=combined_data.get('emission_temp'),
            bv=combined_data.get('battery_voltage')
        )

        msg = f"L:{s['lap_current']};D:{s['time_delta']}"
        data_source.send_to_bolid(msg)

    return jsonify(combined_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=False)
