import sys
import os
import sqlite3
from pathlib import Path

# Add workspace root to Python path for package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from python_news_dashboard import db_helper


def test_initialize_database_creates_tables(tmp_path, monkeypatch):
    db_path = tmp_path / "news_data.db"

    original_connect = sqlite3.connect

    def connect_override(path):
        # Always use the temp DB path regardless of input
        return original_connect(db_path)

    monkeypatch.setattr(db_helper.sqlite3, "connect", connect_override)

    db_helper.initialize_database()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        names = [row[0] for row in cursor.fetchall()]

    assert "daily_tags" in names
    assert "daily_states" in names
    assert "daily_summary" in names


def test_update_and_query_db(tmp_path, monkeypatch):
    db_path = tmp_path / "news_data.db"

    original_connect = sqlite3.connect

    def connect_override(path):
        return original_connect(db_path)

    monkeypatch.setattr(db_helper.sqlite3, "connect", connect_override)
    db_helper.initialize_database()

    date = "2026-03-18"
    tags_data = {"Politik": 5, "Wirtschaft": 3}
    states_data = {"Bayern": 4, "Berlin": 2}
    db_helper.update_tags_in_db(tags_data, date)
    db_helper.update_states_in_db(states_data, date)
    db_helper.update_article_count(date, 7)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM daily_tags WHERE tag='Politik' AND date=?", (date,))
        politik_count = cursor.fetchone()[0]

        cursor.execute("SELECT count FROM daily_states WHERE state='Bayern' AND date=?", (date,))
        bayern_count = cursor.fetchone()[0]

        cursor.execute("SELECT article_count FROM daily_summary WHERE date=?", (date,))
        article_count = cursor.fetchone()[0]

    assert politik_count == 5
    assert bayern_count == 4
    assert article_count == 7
