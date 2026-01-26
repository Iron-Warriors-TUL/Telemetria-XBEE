import csv
import time
import os
from datetime import datetime


class RaceLogger:
    def __init__(self):
        self.laps = []
        self.start_time = None

    def start_race(self):
        self.start_time = datetime.now()

    def log_lap(self, lap_number, lap_time, delta, max_speed):
        self.laps.append({
            "lap": lap_number,
            "lap_time": round(lap_time, 1),
            "delta": round(delta, 1),
            "max_speed": max_speed
        })

    def save_csv(self):
        if not self.laps:
            return None

        os.makedirs("logs", exist_ok=True)

        if self.start_time:
            ts = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        else:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = f"logs/race_{ts}.csv"

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["lap", "lap_time", "delta", "max_speed"]
            )
            writer.writeheader()
            writer.writerows(self.laps)

        return filename

    def reset(self):
        self.laps = []
        self.start_time = None
