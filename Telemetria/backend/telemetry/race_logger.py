import csv
import os
import subprocess
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        ts = self.start_time.strftime(
            "%Y-%m-%d_%H-%M-%S") if self.start_time else datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"logs/race_{ts}.csv"

        with open(filename, "w", newline="") as f:
            f.write(f"# miejsce: {meta.get('place', '-') if meta else '-'}\n")
            f.write(
                f"# kierowca: {meta.get('driver', '-') if meta else '-'}\n")
            f.write(f"# data: {race_date if race_date else ts}\n")
            f.write(
                f"# komentarz: {meta.get('comment', '-') if meta else '-'}\n")

            writer = csv.DictWriter(f, fieldnames=[
                                    'race_time', 'lap_number', 'speed', 'rpm', 'oil', 'clt', 'iat', 'egt', 'bv'])
            writer.writeheader()
            writer.writerows(self.data)
        return filename

    def generate_report_and_push(self, csv_path):
        if not csv_path or not os.path.exists(csv_path):
            return

        metadata = {}
        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    parts = line.replace('#', '').strip().split(': ', 1)
                    if len(parts) == 2:
                        metadata[parts[0]] = parts[1]
                else:
                    break

        df = pd.read_csv(csv_path, comment='#')
        lap_times = df.groupby('lap_number')['race_time'].agg(['min', 'max'])
        lap_times['duration'] = (lap_times['max'] - lap_times['min']).round(2)
        best_lap = lap_times['duration'].idxmin()

        params = [
            ('speed', 'Prędkość (km/h)', 'red'),
            ('rpm', 'Obroty (RPM)', 'cyan'),
            ('oil', 'Temp. Oleju (°C)', 'orange'),
            ('clt', 'Temp. Bloku silnika (°C)', 'green'),
            ('egt', 'EGT (°C)', 'magenta')
        ]

        fig = make_subplots(
            rows=len(params) + 1, cols=1, shared_xaxes=True, vertical_spacing=0.05,
            specs=[[{"type": "table"}]] +
            [[{"type": "scatter"}]] * len(params),
            row_heights=[0.2] + [0.8/len(params)]*len(params),
            subplot_titles=["PODSUMOWANIE"] + [p[1] for p in params]
        )

        # Tabela
        fig.add_trace(go.Table(
            header=dict(values=['Lap', 'Czas (s)'],
                        fill_color='#444', font=dict(color='white')),
            cells=dict(values=[lap_times.index, lap_times['duration']],
                       fill_color=[['#222' for i in lap_times.index]],
                       font=dict(color='white'), align='center')
        ), row=1, col=1)

        # Wykresy
        lap_starts = lap_times['min'].tolist()
        lap_labels = [f"Lap {int(i)}" for i in lap_times.index]

        for i, (col, name, color) in enumerate(params, start=2):
            fig.add_trace(go.Scatter(
                x=df['race_time'], y=df[col], name=name, line=dict(color=color)), row=i, col=1)
            fig.update_xaxes(tickmode='array', tickvals=lap_starts,
                             ticktext=lap_labels, showticklabels=True, row=i, col=1)
            for start in lap_starts:
                fig.add_vline(x=start, line_width=1, line_dash="dash",
                              line_color="rgba(255,255,255,0.2)", row=i, col=1)

        header_html = "<br>".join(
            [f"<b>{k}:</b> {v}" for k, v in metadata.items()])
        fig.update_layout(height=2200, template="plotly_dark", title=dict(text=f"TELEMETRIA XBEE<br>{header_html}", x=0.5, xanchor='center'),
                          margin=dict(t=300), showlegend=False)

        report_path = csv_path.replace(".csv", ".html")
        fig.write_html(report_path)

        self._git_push([csv_path, report_path])

    def _git_push(self, files):
        try:
            subprocess.run(["git", "add"] + files, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Auto-report: {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print(">>> Dane i raport wysłane pomyślnie na GitHub!")
        except Exception as e:
            print(f">>> Błąd Git: {e}")

    def reset(self):
        self.laps = []
        self.data = []
        self.start_time = None
        self.last_record_time = -1.0
