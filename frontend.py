import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geopandas as gpd
import unicodedata
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
DB_PATH = 'news_data.db'
GEOJSON_PATH = "2_hoch.geo.json"
STATE_MAPPING = {
    "Baden-Württemberg": "Baden-Württemberg",
    "Bayern": "Bayern",
    "Berlin": "Berlin",
    "Brandenburg": "Brandenburg",
    "Bremen": "Bremen",
    "Hamburg": "Hamburg",
    "Hessen": "Hessen",
    "Mecklenburg-Vorpommern": "Mecklenburg-Vorpommern",
    "Niedersachsen": "Niedersachsen",
    "Nordrhein-Westfalen": "Nordrhein-Westfalen",
    "Rheinland-Pfalz": "Rheinland-Pfalz",
    "Saarland": "Saarland",
    "Sachsen": "Sachsen",
    "Sachsen-Anhalt": "Sachsen-Anhalt",
    "Schleswig-Holstein": "Schleswig-Holstein",
    "Thüringen": "Thüringen"
}

# Utility function for database queries
def execute_query(query, params=None, fetch_all=True):
    """Execute a database query with optional parameters."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall() if fetch_all else cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return [] if fetch_all else None

def fetch_data():
    """Fetch all data from the 'daily_tags' table."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM daily_tags;")
            return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []

def fetch_top_daily_tags_for_date(date):
    """Fetch top 5 daily tags for a specific date."""
    query = """
        SELECT tag, count 
        FROM daily_tags 
        WHERE date = ? 
        ORDER BY count DESC 
        LIMIT 5;
    """
    return execute_query(query, (date,))

def fetch_daily_summary():
    """Fetch the total number of articles per day for the last 10 days."""
    start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    query = """
        SELECT date, article_count 
        FROM daily_summary 
        WHERE date >= ? 
        ORDER BY date ASC;
    """
    return execute_query(query, (start_date,))

def fetch_top_states_for_date(date):
    """Fetch top 5 states with the highest count for a specific date."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT state, count 
                FROM daily_states 
                WHERE date = ? 
                ORDER BY count DESC 
                LIMIT 5;
            """, (date,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []

def fetch_article_counts_by_state(date):
    """Fetch article counts per state for a specific date."""
    query = """
        SELECT state, count 
        FROM daily_states 
        WHERE date = ?;
    """
    rows = execute_query(query, (date,))
    return {row[0]: row[1] for row in rows}

def populate_treeview(tree, data):
    """Insert data into a Treeview widget."""
    for row in data:
        tree.insert("", "end", values=row)

def create_bar_chart(frame, data):
    """Create and embed a horizontal bar chart in the given tkinter frame."""
    data = sorted(data, key=lambda x: x[1])  # Sort data by count
    tags = [item[0] for item in data]
    counts = [item[1] for item in data]
    
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.barh(tags, counts, color="skyblue")
    ax.set_title("Anzahl der Artikel pro Kategorie")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=20, pady=20)

def create_line_chart(frame, data, title):
    """Create and embed a line chart in the given tkinter frame."""
    dates = [datetime.strptime(item[0], "%Y-%m-%d").strftime("%d.%m.%Y") for item in data]
    totals = [item[1] for item in data]
    
    title_label = tk.Label(frame, text=title, font=("Arial", 18, "bold"))
    title_label.pack(anchor="n", pady=(10, 0))

    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(dates, totals, marker="o", linestyle="-", color="blue")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=20, pady=20)

def normalize_state_name(name):
    """Normalize state names to ASCII."""
    return name

def create_germany_map(frame, geojson_path, data, date):
    """Create and embed a map of Germany with article counts in the given tkinter frame."""
    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        logging.error(f"Error loading GeoJSON file: {e}")
        return

    rows = execute_query("""
        SELECT state, count 
        FROM daily_states 
        WHERE date = ?;
    """, (date,))
    for state, count in rows:
        data[state] = count

    normalized_data = {normalize_state_name(state): count for state, count in data.items()}
    mapped_data = {STATE_MAPPING.get(state, state): count for state, count in normalized_data.items()}

    logging.info(f"Artikelanzahl pro Bundesland am {date}:")
    for state, count in mapped_data.items():
        logging.info(f"{state}: {count}")

    gdf['count'] = gdf['name'].map(mapped_data).fillna(0)

    current_date_formatted = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
    title_text = f"Veröffentlichte Artikel pro Bundesland am {current_date_formatted}"

    title_label = tk.Label(frame, text=title_text, font=("Arial", 18, "bold"))
    title_label.pack(anchor="n", pady=(10, 0))

    fig, ax = plt.subplots(figsize=(4, 4))
    gdf.plot(column='count', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
    ax.axis('off')
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(anchor="center", padx=20, pady=20)

def update_time():
    """Update the time in the welcome label."""
    current_datetime = datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.now().strftime("%H:%M:%S")
    welcome_text = f"Herzlich Willkommen Herr Mustermann.\nHeute ist der {current_datetime}.\nEs ist {current_time}."
    welcome_label.config(text=welcome_text.replace("\n", " "))
    root.after(1000, update_time)

def update_top_right_graph(graph_type):
    """Update the graph and button states in the top-right section."""
    for widget in stats_top_right_frame.winfo_children():
        widget.destroy()

    button_frame = tk.Frame(stats_top_right_frame)
    button_frame.pack(anchor="n", pady=5)

    schlagworte_button = tk.Button(
        button_frame, text="Schlagworte", font=("Arial", 18, "bold"),
        relief="sunken" if graph_type == "Schlagworte" else "raised",
        command=lambda: update_top_right_graph("Schlagworte")
    )
    schlagworte_button.grid(row=0, column=0, padx=10, pady=5)

    bundeslaender_button = tk.Button(
        button_frame, text="Bundesländer", font=("Arial", 18, "bold"),
        relief="sunken" if graph_type == "Bundesländer" else "raised",
        command=lambda: update_top_right_graph("Bundesländer")
    )
    bundeslaender_button.grid(row=0, column=1, padx=10, pady=5)

    current_date_formatted = datetime.strptime(current_date, "%Y-%m-%d").strftime("%d.%m.%Y")

    if graph_type == "Schlagworte":
        stats_top_right_label = tk.Label(
            stats_top_right_frame,
            text=f"Diese Themenbereiche waren am {current_date_formatted} hochrelevant:",
            font=("Arial", 16, "bold"),
            anchor="center"
        )
        stats_top_right_label.pack(anchor="center", padx=5, pady=5)

        top_tags = fetch_top_daily_tags_for_date(current_date)
        create_bar_chart(stats_top_right_frame, top_tags)

    elif graph_type == "Bundesländer":
        stats_top_right_label = tk.Label(
            stats_top_right_frame,
            text=f"Diese Bundesländer waren am {current_date_formatted} hochrelevant:",
            font=("Arial", 16, "bold"),
            anchor="center"
        )
        stats_top_right_label.pack(anchor="center", padx=5, pady=5)

        top_states = fetch_top_states_for_date(current_date)
        create_bar_chart(stats_top_right_frame, top_states)

def populate_date_dropdown():
    """Generate a list of dates for the dropdown menu based on available DB data."""
    rows = execute_query("""
        SELECT DISTINCT date
        FROM (
            SELECT date FROM daily_summary
            UNION
            SELECT date FROM daily_tags
            UNION
            SELECT date FROM daily_states
        )
        ORDER BY date ASC;
    """)

    if rows:
        return [datetime.strptime(row[0], "%Y-%m-%d").strftime("%d.%m.%Y") for row in rows]

    start_date = datetime(2026, 3, 8)
    end_date = datetime.now()
    return [(start_date + timedelta(days=i)).strftime("%d.%m.%Y") for i in range((end_date - start_date).days + 1)]

def get_initial_current_date():
    """Get the newest available date from DB, fallback to today."""
    rows = execute_query("""
        SELECT MAX(date)
        FROM (
            SELECT date FROM daily_summary
            UNION
            SELECT date FROM daily_tags
            UNION
            SELECT date FROM daily_states
        );
    """, fetch_all=False)

    if rows and rows[0]:
        return rows[0]

    return datetime.now().strftime("%Y-%m-%d")

current_date = get_initial_current_date()

def update_graphs_and_labels(new_date):
    """Update graphs and labels when the date is changed."""
    global current_date
    current_date = datetime.strptime(new_date, "%d.%m.%Y").strftime("%Y-%m-%d")
    update_top_right_graph("Schlagworte")
    for widget in stats_bottom_right_frame.winfo_children():
        widget.destroy()
    article_counts = fetch_article_counts_by_state(current_date)
    create_germany_map(stats_bottom_right_frame, GEOJSON_PATH, article_counts, current_date)

def export_to_excel():
    """Export data to an Excel file."""
    import pandas as pd
    from pathlib import Path
    downloads_dir = Path.home() / "Downloads"
    db_path = 'news_data.db'
    connection = sqlite3.connect(db_path)
    query_tags = """
        SELECT tag, count 
        FROM daily_tags 
        WHERE date = ? 
        ORDER BY count DESC 
        LIMIT 5;
    """
    data_tags = pd.read_sql_query(query_tags, connection, params=(current_date,))
    query_states = """
        SELECT state, count 
        FROM daily_states 
        WHERE date = ? 
        ORDER BY count DESC 
        LIMIT 5;
    """
    data_states = pd.read_sql_query(query_states, connection, params=(current_date,))
    query_summary = """
        SELECT date, article_count 
        FROM daily_summary 
        WHERE date >= ? 
        ORDER BY date ASC;
    """
    start_date = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=10)).strftime("%Y-%m-%d")
    data_summary = pd.read_sql_query(query_summary, connection, params=(start_date,))
    query_map = """
        SELECT state, count 
        FROM daily_states 
        WHERE date = ?;
    """
    data_map = pd.read_sql_query(query_map, connection, params=(current_date,))
    connection.close()
    file_name = downloads_dir / f"news_dashboard_data_{current_date}.xlsx"
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        data_tags.to_excel(writer, sheet_name="Schlagworte", index=False)
        data_states.to_excel(writer, sheet_name="Bundesländer", index=False)
        data_summary.to_excel(writer, sheet_name="Tägliche Zusammenfassung", index=False)
        data_map.to_excel(writer, sheet_name="Bundesländer Zusammenfassung", index=False)
    print(f"Data exported to {file_name}")

# Main tkinter window
root = tk.Tk()
root.title("News Dashboard")

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Welcome text (top-left)
welcome_frame = tk.Frame(root, borderwidth=2, relief="groove")
welcome_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

heading_label = tk.Label(welcome_frame, text="German News Dashboard", font=("Arial", 24, "bold"), pady=10)
heading_label.pack()

welcome_label = tk.Label(welcome_frame, font=("Arial", 18), wraplength=400, justify="center")
welcome_label.pack(expand=True)

update_time()

date_options = populate_date_dropdown()
selected_date = tk.StringVar(value=datetime.strptime(current_date, "%Y-%m-%d").strftime("%d.%m.%Y"))
date_dropdown = tk.OptionMenu(
    welcome_frame, selected_date, *date_options,
    command=lambda new_date: update_graphs_and_labels(new_date)
)
date_dropdown.config(font=("Arial", 18, "bold"), relief="raised", width=20, justify="center")
menu = date_dropdown.nametowidget(date_dropdown.menuname)
menu.config(font=("Arial", 12))
date_dropdown.pack(pady=10)

excel_export_button = tk.Button(
    welcome_frame, text="Excel Export", font=("Arial", 18, "bold"),
    command=export_to_excel
)
excel_export_button.pack(pady=10)

# Statistics (top-right)
stats_top_right_frame = tk.Frame(root, borderwidth=2, relief="groove")
stats_top_right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

button_frame = tk.Frame(stats_top_right_frame)
button_frame.pack(anchor="n", pady=5)

schlagworte_button = tk.Button(
    button_frame, text="Schlagworte", font=("Arial", 12), relief="sunken",
    command=lambda: update_top_right_graph("Schlagworte")
)
schlagworte_button.grid(row=0, column=0, padx=10, pady=5)

bundeslaender_button = tk.Button(
    button_frame, text="Bundesländer", font=("Arial", 12), relief="raised",
    command=lambda: update_top_right_graph("Bundesländer")
)
bundeslaender_button.grid(row=0, column=1, padx=10, pady=5)

current_date_formatted = datetime.strptime(current_date, "%Y-%m-%d").strftime("%d.%m.%Y")
stats_top_right_label = tk.Label(
    stats_top_right_frame, 
    text=f"Diese Themenbereiche waren am {current_date_formatted} brandaktuell.", 
    font=("Arial", 18, "bold")
)
stats_top_right_label.pack(anchor="w", padx=5, pady=5)

update_top_right_graph("Schlagworte")

# Statistics (bottom-left)
stats_bottom_left_frame = tk.Frame(root, borderwidth=2, relief="groove")
stats_bottom_left_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=(10, 20))

daily_summary_data = fetch_daily_summary()
create_line_chart(stats_bottom_left_frame, daily_summary_data, "Gesamtanzahl der Artikel (letzte 10 Tage)")

# Statistics (bottom-right)
stats_bottom_right_frame = tk.Frame(root, borderwidth=2, relief="groove")
stats_bottom_right_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10, 20))

article_counts = fetch_article_counts_by_state(current_date)
create_germany_map(stats_bottom_right_frame, GEOJSON_PATH, article_counts, current_date)

root.mainloop()