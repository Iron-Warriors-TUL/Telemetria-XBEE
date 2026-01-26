import math


class MockTelemetrySource:
    def get_sample(self, lap_phase, elapsed):
        rpm = int(2000 + (math.sin(lap_phase) + 1) / 2 * 5000)
        speed = int((rpm / 7000) * 60)

        engine_temp = int(75 + elapsed / 60 * 0.4)
        oil_temp = int(70 + elapsed / 60 * 0.3)

        return {
            "rpm": rpm,
            "speed": speed,
            "engine_temp": engine_temp,
            "oil_temp": oil_temp
        }
