from flask import Flask, jsonify, request, render_template
from telemetry.race_state import RaceState
from telemetry.data_source import MockTelemetrySource
from telemetry.race_logger import RaceLogger

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

data_source = MockTelemetrySource()
logger = RaceLogger()
race = RaceState(data_source, logger)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/state")
def state():
    return jsonify(race.get_state())


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


if __name__ == "__main__":
    app.run(debug=True)
