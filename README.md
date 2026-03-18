# Python News Dashboard

## 📌 Projektübersicht

`python_news_dashboard` ist ein Python-basiertes Dashboard, das Tagesschau-Nachrichtendaten (API) analysiert und speichert. Das Projekt beinhaltet:

- Tägliche Datenabfrage und Datenanalyse (Tags + Bundesländer)
- Speicherung in SQLite (`news_data.db`)
- Lokale Tkinter-basierte Desktop-Visualisierung mit Kartendarstellung


## 🧭 Architektur

1. `main.py`: Hauptprozess, der die Tagesschau-Daten automatisch abruft und in DB speichert.
2. `analyze.py`: Daten-Extraktion, Tag-/Region-Analyse und Filterlogik.
3. `database_helper.py`: SQLite-Initialisierung und Speicherung in Tabellen.
4. `frontend.py`: Tkinter-GUI mit Diagrammen (Matplotlib) und GeoJSON-Karte.
4. `frontend.py`: Tkinter-GUI mit Diagrammen (Matplotlib) und GeoJSON-Karte.


## 🚀 Schnellstart

### 1) Repository navigieren

```bash
cd python_news_dashboard
```

### 2) Virtuelle Umgebung 

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3) Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

> Hinweis: Für die GUI (`frontend.py`) werden zusätzliche Bibliotheken benötigt:
> - `matplotlib`
> - `geopandas`
> - `pandas`
> - `tkinter`

Installieren bei Bedarf:

```bash
pip install matplotlib geopandas pandas
```

### 4) Ersten Lauf testen (Entwicklungsmodus)

```bash
python main.py
```

`main.py` startet im Produktionsmodus und wiederholt jeden Tag. Für lokalen Debug mit `test-data.json` kannst du `develop_mode=True` im `main.py`-Aufruf setzen.


## 🧪 Datenbank-Setup

Die SQLite-Datenbank `news_data.db` wird automatisch erstellt, wenn du `main.py` ausführst (über `initialize_database()`).

Tabellen:
- `daily_tags` (`date`, `tag`, `count`)
- `daily_states` (`date`, `state`, `count`)
- `daily_summary` (`date`, `article_count`)


## 🖥️ Desktop-Frontend

Starte das GUI:

```bash
python frontend.py
```

Das GUI zeigt:
- Top-Schlagworte
- Analyse pro Bundesland
- Zeitreihe Artikelanzahl
- Deutschlandkarte



## 🧪 Tests

Um Unit-Tests auszuführen:

```bash
cd python_news_dashboard
pytest -q
```

Die Tests prüfen die Kernlogik in `analyze.py` und die Datenbankfunktionalität in `db_helper.py`.

## 🔧 Wichtige Dateien

- `main.py` – Orchestrator für API-Abruf, Analyse, DB-Update
- `analyze.py` – Logik für Tag- und Region-Analyse
- `db_helper.py` – DB-Initialisierung und Insert-Funktionen
- `frontend.py` – Tkinter-Auswertung & Visualisierung
- `2_hoch.geo.json` – GeoJSON für Bundesländerkarte


## 📝 Entwicklungshinweise

- Wenn die API keine Daten liefert, enthält `main.py` eine Retry-Schleife (60s) und läuft weiter.
- In `analyze.py` sind Tags aus `EXCLUDE_TAGS` gefiltert und nur Tags mit mindestens 3 Vorkommen werden in `filtered_tags` übernommen.
- `main.py` fügt jeden Tag neue Zeilen ein (keine deduplizierten Inserts).


## 🧭 Erweiterungsmöglichkeiten

- DB-Deduplizierung nach (Datum + Tag/Bundesland)
- Hintergrundscheduler statt `time.sleep(86400)` (z.B. APScheduler)
- Einheitliches Config-File (`config.py` oder `.env`)
- Frontend als Web-Dashboard (z.B. Dash / Streamlit)


## 🔐 Lizenz

Dieses Projekt ist unter keiner speziellen Lizenz in diesem Repo definiert. Füge ggf. eine `LICENSE`-Datei hinzu.
