import csv
from datetime import datetime

class RaceRecorder:
    def __init__(self):
        self.laps = []

    def record_lap(self, lap_number, lap_time, time_delta, max_speed):
        self.laps.append({
            "lap": lap_number,
            "lap_time": lap_time,
            "time_delta": time_delta,
            "max_speed": max_speed
        })

    def save_csv(self):
        if not self.laps:
            return None

        filename = f"race_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["lap", "lap_time", "time_delta", "max_speed"]
            )
            writer.writeheader()
            writer.writerows(self.laps)

        return filename
