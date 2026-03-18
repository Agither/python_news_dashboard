import sqlite3
from datetime import datetime

def initialize_database():
    """
    Initialisiert die SQLite-Datenbank, falls sie nicht existiert, mit drei Tabellen:
    daily_tags, daily_states und daily_summary.
    """
    connection = sqlite3.connect("news_data.db")
    cursor = connection.cursor()

    # Tabelle für tägliche Tags erstellen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        tag TEXT NOT NULL,
        count INTEGER NOT NULL
    )
    """)

    # Tabelle für tägliche Bundesländer erstellen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        state TEXT NOT NULL,
        count INTEGER NOT NULL
    )
    """)

    # Neue Tabelle für tägliche Artikelanzahl erstellen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        article_count INTEGER NOT NULL
    )
    """)

    connection.commit()
    connection.close()

def update_tags_in_db(tags_data, date):
    """
    Speichert die Tags für ein bestimmtes Datum in der Datenbank.

    :param tags_data: Dictionary der Tags mit ihren Vorkommenszahlen.
    :param date: Datum, für welches die Werte gesichert werden.
    """
    connection = sqlite3.connect("news_data.db")
    cursor = connection.cursor()

    for tag, count in tags_data.items():
        # Tags mit Datum speichern
        cursor.execute("INSERT INTO daily_tags (date, tag, count) VALUES (?, ?, ?)", (date, tag, count))

    connection.commit()
    connection.close()

def update_states_in_db(state_data, date):
    """
    Speichert die Bundesländer für ein bestimmtes Datum in der Datenbank.

    :param state_data: Counter der Bundesländer mit ihren Vorkommenszahlen.
    :param date: Datum, für welches die Werte gesichert werden.
    """
    connection = sqlite3.connect("news_data.db")
    cursor = connection.cursor()

    for state, count in state_data.items():
        # Bundesländer mit Datum speichern
        cursor.execute("INSERT INTO daily_states (date, state, count) VALUES (?, ?, ?)", (date, state, count))

    connection.commit()
    connection.close()

def update_article_count(date, article_count):
    """
    Speichert die Gesamtanzahl der Artikel für ein bestimmtes Datum in der Datenbank.

    :param date: Datum, für das die Anzahl der Artikel gespeichert wird.
    :param article_count: Anzahl der Artikel an diesem Datum.
    """
    connection = sqlite3.connect("news_data.db")
    cursor = connection.cursor()

    # Artikelanzahl mit Datum speichern
    cursor.execute("INSERT INTO daily_summary (date, article_count) VALUES (?, ?)", (date, article_count))

    connection.commit()
    connection.close()

def get_current_date():
    """
    Gibt das aktuelle Datum im Format YYYY-MM-DD zurück.
    """
    return datetime.now().strftime("%Y-%m-%d")