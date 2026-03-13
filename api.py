from flask import Flask, jsonify, request
import sqlite3

# Flask-App initialisieren
app = Flask(__name__)

# SQL-Datenbank-Datei
DATABASE = "news_data.db"

# Helper-Funktion: Verbindung zur Datenbank
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row  # Ermöglicht Zugriff als Dictionary
    return connection

# -------------------------------
# API-Endpunkte
# -------------------------------

# **GET /api/tags**
@app.route('/api/tags', methods=['GET'])
def get_tags():
    try:
        conn = get_db_connection()
        query = "SELECT date, tag, count FROM daily_tags"
        results = conn.execute(query).fetchall()
        conn.close()

        # Konvertiere die Ergebnisse in JSON-Format
        tags = [{"date": row["date"], "tag": row["tag"], "count": row["count"]} for row in results]

        if tags:
            return jsonify(tags), 200
        else:
            return jsonify({"error": "Keine Daten verfügbar."}), 404
    except Exception as e:
        return jsonify({"error": f"Interner Serverfehler: {str(e)}"}), 500

# **GET /api/states**
@app.route('/api/states', methods=['GET'])
def get_states():
    try:
        conn = get_db_connection()
        query = "SELECT date, state, count FROM daily_states"
        results = conn.execute(query).fetchall()
        conn.close()

        # Konvertiere die Ergebnisse in JSON-Format
        states = [{"date": row["date"], "state": row["state"], "count": row["count"]} for row in results]

        if states:
            return jsonify(states), 200
        else:
            return jsonify({"error": "Keine Daten verfügbar."}), 404
    except Exception as e:
        return jsonify({"error": f"Interner Serverfehler: {str(e)}"}), 500

# **GET /api/articles**
@app.route('/api/articles', methods=['GET'])
def get_articles():
    try:
        conn = get_db_connection()
        query = "SELECT date, article_count FROM daily_summary"
        results = conn.execute(query).fetchall()
        conn.close()

        # Konvertiere die Ergebnisse in JSON-Format
        articles = [{"date": row["date"], "article_count": row["article_count"]} for row in results]

        if articles:
            return jsonify(articles), 200
        else:
            return jsonify({"error": "Keine Daten verfügbar."}), 404
    except Exception as e:
        return jsonify({"error": f"Interner Serverfehler: {str(e)}"}), 500


# **GET /api/tags/<date>**
@app.route('/api/tags/<date>', methods=['GET'])
def get_tags_by_date(date):
    try:
        conn = get_db_connection()
        query = "SELECT tag, count FROM daily_tags WHERE date = ?"
        results = conn.execute(query, (date,)).fetchall()
        conn.close()

        # Konvertiere die Ergebnisse in JSON-Format
        tags = [{"tag": row["tag"], "count": row["count"]} for row in results]

        if tags:
            return jsonify(tags), 200
        else:
            return jsonify({"error": f"Keine Daten für {date} verfügbar."}), 404
    except Exception as e:
        return jsonify({"error": f"Interner Serverfehler: {str(e)}"}), 500


# **GET /api/states/<date>**
@app.route('/api/states/<date>', methods=['GET'])
def get_states_by_date(date):
    try:
        conn = get_db_connection()
        query = "SELECT state, count FROM daily_states WHERE date = ?"
        results = conn.execute(query, (date,)).fetchall()
        conn.close()

        # Konvertiere die Ergebnisse in JSON-Format
        states = [{"state": row["state"], "count": row["count"]} for row in results]

        if states:
            return jsonify(states), 200
        else:
            return jsonify({"error": f"Keine Daten für {date} verfügbar."}), 404
    except Exception as e:
        return jsonify({"error": f"Interner Serverfehler: {str(e)}"}), 500


# **GET /api/articles/<date>**
@app.route('/api/articles/<date>', methods=['GET'])
def get_articles_by_date(date):
    try:
        conn = get_db_connection()
        query = "SELECT article_count FROM daily_summary WHERE date = ?"
        result = conn.execute(query, (date,)).fetchone()
        conn.close()

        if result:
            return jsonify({"date": date, "article_count": result["article_count"]}), 200
        else:
            return jsonify({"error": f"Keine Daten für {date} verfügbar."}), 404
    except Exception as e:
        return jsonify({"error": f"Interner Serverfehler: {str(e)}"}), 500

# -------------------------------
# Hauptblock
# -------------------------------

if __name__ == "__main__":
    app.run(debug=False)