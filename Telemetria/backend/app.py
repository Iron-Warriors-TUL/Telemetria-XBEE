from flask import Flask, jsonify, request, render_template
from telemetry.race_state import RaceState
from telemetry.data_source import XBeeTelemetrySource
from telemetry.race_logger import RaceLogger

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

data_source = XBeeTelemetrySource(port="/dev/serial0", baud=115200)
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
    filename = logger.save_csv()
    return jsonify({"file": filename})

@app.route("/api/state")
def state():
    s = race.get_state()
    
    # Jeśli wyścig trwa, wyślij dane do bolidu
    if s.get("running"):
        # Format: L:numer_okrążenia;D:delta
        # Używamy skróconych kluczy, by oszczędzać pasmo
        msg = f"L:{s['lap_current']};D:{s['time_delta']}"
        data_source.send_to_bolid(msg)
        
    return jsonify(s)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
