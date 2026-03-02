import csv
import os
from datetime import datetime


class RaceLogger:
    def __init__(self):
        self.laps = []
        self.data = []
        self.start_time = None
        self.last_record_time = -1.0

    def start_race(self):
        self.start_time = datetime.now()
        self.last_record_time = -0.5

    def log_data(self, race_time, interval=0.5, **kwargs):
        if race_time - self.last_record_time >= interval:
            entry = {'race_time': round(race_time, 2)}
            entry.update(kwargs)
            self.data.append(entry)
            self.last_record_time = race_time
            return True
        return False

    def save_csv(self, meta=None):
        if not self.data:
            return None

        os.makedirs("logs", exist_ok=True)

        race_date = meta.get('date', '').replace('T', ' ') if meta else None

        if self.start_time:
            ts = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        else:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = f"logs/race_{ts}.csv"

        with open(filename, "w", newline="") as f:
            f.write(f"# data: {race_date if race_date else ts}\n")
            f.write(f"# kierowca: {meta.get('driver', '-') if meta else '-'}\n")
            f.write(f"# miejsce: {meta.get('place', '-') if meta else '-'}\n")
            f.write(f"# komentarz: {meta.get('comment', '-') if meta else '-'}\n")

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    'race_time',
                    'lap_number',
                    'speed',
                    'rpm',
                    'oil',
                    'clt',
                    'iat',
                    'egt',
                    'bv'
                ]
            )
            writer.writeheader()
            writer.writerows(self.data)

        return filename

    def reset(self):
        self.laps = []
        self.data = []
        self.start_time = None
        self.last_record_time = -1.0
