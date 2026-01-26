import time
import math


class RaceState:
    def __init__(self, data_source, logger):
        self.data_source = data_source
        self.logger = logger

        self.configured = False
        self.running = False
        self.finished = False

        self.target_lap_time = 0
        self.max_laps = 0

        self.start_time = None
        self.lap_start_time = None

        self.current_lap = 1
        self.final_delta = None
        self.max_speed_current_lap = 0

    def configure(self, lap_target_time, max_laps):
        self.target_lap_time = lap_target_time
        self.max_laps = max_laps
        self.configured = True
        self.running = False
        self.finished = False
        self.current_lap = 1
        self.start_time = None
        self.lap_start_time = None
        self.final_delta = None
        self.logger.reset()

    def start(self):
        if not self.configured or self.finished:
            return
        self.running = True
        now = time.time()
        self.start_time = now
        self.lap_start_time = now
        self.max_speed_current_lap = 0

        self.logger.start_race()

    def reset(self):
        self.__init__(self.data_source, self.logger)

    def change_lap(self, delta):
        if not self.running:
            return

        if delta > 0:
            now = time.time()
            lap_time = now - self.lap_start_time
            expected = self.target_lap_time
            delta_time = expected - lap_time

            self.logger.log_lap(
                self.current_lap,
                lap_time,
                delta_time,
                self.max_speed_current_lap
            )

            if self.current_lap >= self.max_laps:
                self.running = False
                self.finished = True
                self.final_delta = delta_time
                return

            self.current_lap += 1
            self.lap_start_time = now
            self.max_speed_current_lap = 0

        elif delta < 0:
            self.current_lap = max(1, self.current_lap - 1)

    def get_state(self):
        if not self.configured:
            return {"running": False}

        if self.finished:
            return {
                "running": False,
                "finished": True,
                "time_delta": round(self.final_delta, 1)
            }

        if not self.running:
            return {
                "running": False,
                "lap_current": self.current_lap,
                "lap_total": self.max_laps
            }

        now = time.time()
        elapsed = now - self.start_time
        lap_elapsed = now - self.lap_start_time

        lap_phase = (lap_elapsed / self.target_lap_time) * 2 * math.pi
        sample = self.data_source.get_sample(lap_phase, elapsed)

        self.max_speed_current_lap = max(
            self.max_speed_current_lap,
            sample["speed"]
        )

        race_target_time = self.target_lap_time * self.max_laps

        return {
            "running": True,

            "lap_current": self.current_lap,
            "lap_total": self.max_laps,

            "lap_time": round(lap_elapsed, 1),
            "lap_time_remaining": round(self.target_lap_time - lap_elapsed, 1),

            "race_time_remaining": round(race_target_time - elapsed, 1),

            "time_delta": round(
                (self.current_lap * self.target_lap_time) - elapsed, 1
            ), 

            **sample
        }
