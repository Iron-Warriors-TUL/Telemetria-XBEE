import threading
import time
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress


class XBeeTelemetrySource:
    def __init__(self, port="/dev/serial0", baud=115200):
        # Stan początkowy zgodny z dashboard.html
        self.data = {
            "rpm": 0,
            "speed": 0,
            "engine_temp": 0,
            "oil_temp": 0,
            "intake_temp": 0,
            "emission_temp": 0,
            "battery_voltage": 0.0
        }

        # Adres XBee w bolidzie
        self.bolid_address = "0013A20042411A98"
        self.remote_bolid = None

        self.device = XBeeDevice(port, baud)
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def _listen(self):
        try:
            self.device.open()

            # Tworzymy obiekt zdalnego urządzenia (bolidu) do wysyłki duplex
            self.remote_bolid = RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(self.bolid_address))

            # Czyszczenie bufora na starcie, aby uniknąć lagów
            if hasattr(self.device, '_serial_port'):
                self.device._serial_port.reset_input_buffer()

            def on_data_received(msg):
                try:
                    p = msg.data.decode("utf8")
                    d = dict(item.split(":") for item in p.split(";"))

                    # Mapowanie danych przychodzących z bolidu
                    self.data["rpm"] = int(d.get("R", 0))
                    self.data["speed"] = int(d.get("S", 0))
                    self.data["oil_temp"] = int(d.get("OT", 0))
                    self.data["engine_temp"] = int(d.get("CLT", 0))
                    self.data["intake_temp"] = int(d.get("IAT", 0))
                    self.data["emission_temp"] = int(d.get("EGT", 0))
                    self.data["battery_voltage"] = float(d.get("V", 0.0))
                except Exception as e:
                    print(f"Błąd parsowania danych z bolidu: {e}")

            self.device.add_data_received_callback(on_data_received)

            # Podtrzymanie wątku
            while True:
                time.sleep(1)

        except Exception as e:
            print(f"Błąd krytyczny XBee (Odbiornik): {e}")
        finally:
            if self.device.is_open():
                self.device.close()

    def send_to_bolid(self, message):
        """Metoda do wysyłania danych zwrotnych do bolidu (np. delty)"""
        if self.device.is_open() and self.remote_bolid:
            try:
                # Wysyłka Unicast do konkretnego adresu
                self.device.send_data(self.remote_bolid, message)
            except Exception as e:
                print(f"Nie udało się wysłać danych do bolidu: {e}")

    def get_sample(self, lap_phase, elapsed):
        # Metoda wymagana przez race_state.py
        return self.data
