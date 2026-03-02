import math


class MockTelemetrySource:
    def get_sample(self, lap_phase, elapsed):
        rpm = int(2000 + (math.sin(lap_phase) + 1) / 2 * 5000)
        speed = int((rpm / 7000) * 60)

        return {
            "rpm": rpm,
            "speed": speed,
            "engine_temp": int(95 + math.sin(elapsed/10)*5),
            "oil_temp": int(105 + math.cos(elapsed/10)*5),
            "intake_temp": 35,
            "emission_temp": 600,
            "battery_voltage": 14.2
        }

    def send_to_bolid(self, message):
        print(f"DEBUG: Wysłano do bolidu: {message}")
