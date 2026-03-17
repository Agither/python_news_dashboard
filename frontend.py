import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geopandas as gpd  # Import GeoPandas for handling GeoJSON files
import unicodedata  # For normalizing state names

# Mapping of state names in the database to state names in the GeoJSON file
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

# Function to fetch data from the database
def fetch_data():
    db_path = 'news_data.db' 
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Fetch data from the 'daily_tags' table
    cursor.execute("SELECT * FROM daily_tags;")
    rows = cursor.fetchall()
    
    connection.close()
    return rows

# Function to fetch top 5 daily_tags for a specific date
def fetch_top_daily_tags_for_date():
    db_path = 'news_data.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Calculate yesterday's date
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Fetch tags with the highest count for yesterday's date
    cursor.execute("""
        SELECT tag, count 
        FROM daily_tags 
        WHERE date = ? 
        ORDER BY count DESC 
        LIMIT 5;
    """, (yesterday_date,))
    rows = cursor.fetchall()
    
    connection.close()
    return rows

# Function to fetch the total number of articles per day for the last 10 days
def fetch_daily_summary():
    db_path = 'news_data.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Calculate the date 10 days ago
    start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    
    # Fetch the total number of articles per day for the last 10 days
    cursor.execute("""
        SELECT date, article_count 
        FROM daily_summary 
        WHERE date >= ? 
        ORDER BY date ASC;
    """, (start_date,))
    rows = cursor.fetchall()
    
    connection.close()
    return rows

# Function to fetch top 5 states for a specific date
def fetch_top_states_for_date():
    db_path = 'news_data.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Calculate yesterday's date
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Fetch top 5 states with the highest count for yesterday's date
    cursor.execute("""
        SELECT state, count 
        FROM daily_states 
        WHERE date = ? 
        ORDER BY count DESC 
        LIMIT 5;
    """, (yesterday_date,))
    rows = cursor.fetchall()
    
    connection.close()
    return rows

# Function to fetch article counts per state for a specific date
def fetch_article_counts_by_state(date):
    db_path = 'news_data.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Fetch article counts for each state on the given date
    cursor.execute("""
        SELECT state, count 
        FROM daily_states 
        WHERE date = ?;
    """, (date,))
    rows = cursor.fetchall()
    
    connection.close()
    return {row[0]: row[1] for row in rows}  # Convert to dictionary {state: count}

# Function to populate the Treeview with data
def populate_treeview(tree, data):
    for row in data:
        tree.insert("", "end", values=row)

# Function to create a bar chart
def create_bar_chart(frame, data):

    
    # Sort data by count in ascending order
    data = sorted(data, key=lambda x: x[1])  # Ascending order
    tags = [item[0] for item in data]
    counts = [item[1] for item in data]
    
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 3.5))  # Adjusted figure size
    ax.barh(tags, counts, color="skyblue")  # Use horizontal bars
    ax.set_title("Anzahl der Artikel pro Kategorie")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Ensure only integers on the x-axis
    plt.tight_layout()  # Automatically adjust spacing to prevent clipping

    # Embed the plot in the tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=20, pady=20)  # Add padding around the graph

# Function to create a line chart
def create_line_chart(frame, data, title):
    dates = [datetime.strptime(item[0], "%Y-%m-%d").strftime("%d.%m.%Y") for item in data]  # Format dates
    totals = [item[1] for item in data]
    
    # Add title above the graph
    title_label = tk.Label(frame, text=title, font=("Arial", 18, "bold"))
    title_label.pack(anchor="n", pady=(10, 0))  # Add padding above the graph

    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(dates, totals, marker="o", linestyle="-", color="blue")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()  # Automatically adjust spacing to prevent clipping

    # Embed the plot in the tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Function to normalize state names
def normalize_state_name(name):
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")

# Function to create a map of Germany with article counts
def create_germany_map(frame, geojson_path, data, date):
    # Load GeoJSON file
    gdf = gpd.read_file(geojson_path)
    
    # Fetch the counts for all states dynamically from the database
    db_path = 'news_data.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT state, count 
        FROM daily_states 
        WHERE date = ?;
    """, (date,))
    rows = cursor.fetchall()
    connection.close()
    
    # Update the data dictionary with the fetched results
    for state, count in rows:
        data[state] = count
    
    # Normalize state names in the data
    normalized_data = {normalize_state_name(state): count for state, count in data.items()}
    
    # Map the state names in the data to the GeoJSON state names
    mapped_data = {STATE_MAPPING.get(state, state): count for state, count in normalized_data.items()}
    
    # Log the article counts per state
    print(f"Artikelanzahl pro Bundesland am {date}:")
    for state, count in mapped_data.items():
        print(f"{state}: {count}")
    
    # Merge GeoJSON data with article counts
    gdf['count'] = gdf['name'].map(mapped_data).fillna(0)  # Match by state name
    
    # Format the date for the title
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
    title_text = f"Veröffentlichte Artikel pro Bundesland am {formatted_date}"
    
    title_label = tk.Label(frame, text=title_text, font=("Arial", 18, "bold"))
    title_label.pack(anchor="n", pady=(10, 0))  # Add padding above the graph
    
    # Plot the map
    fig, ax = plt.subplots(figsize=(4, 4))  # Adjusted figure size
    gdf.plot(column='count', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
    ax.axis('off')  # Turn off axis
    plt.tight_layout()  # Automatically adjust spacing to prevent clipping

    # Embed the plot in the tkinter frame and center it
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(anchor="center", padx=20, pady=20)  # Add padding around the graph

# Function to update the time in the welcome label
def update_time():
    current_datetime = datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.now().strftime("%H:%M:%S")
    welcome_text = f"Herzlich Willkommen Herr Mustermann.\nHeute ist der {current_datetime}.\nEs ist {current_time}."
    welcome_label.config(text=welcome_text.replace("\n", " "))  # Combine into one line
    root.after(1000, update_time)  # Schedule the function to run again after 1 second

# Function to update the graph and button states in the top-right section
def update_top_right_graph(graph_type):
    # Clear all widgets in the stats_top_right_frame
    for widget in stats_top_right_frame.winfo_children():
        widget.destroy()

    # Recreate the button frame
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

    # Calculate yesterday's date in dd.mm.yyyy format
    yesterday_date_formatted = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")

    # Display the appropriate title and graph
    if graph_type == "Schlagworte":
        stats_top_right_label = tk.Label(
            stats_top_right_frame,
            text=f"Diese Themenbereiche waren gestern, am {yesterday_date_formatted}, hochrelevant:",
            font=("Arial", 16, "bold"),
            anchor="center"
        )
        stats_top_right_label.pack(anchor="center", padx=5, pady=5)

        # Fetch and display the Schlagworte graph
        top_tags = fetch_top_daily_tags_for_date()
        create_bar_chart(stats_top_right_frame, top_tags)

    elif graph_type == "Bundesländer":
        stats_top_right_label = tk.Label(
            stats_top_right_frame,
            text=f"Diese Bundesländer waren gestern, am {yesterday_date_formatted}, hochrelevant:",
            font=("Arial", 16, "bold"),
            anchor="center"
        )
        stats_top_right_label.pack(anchor="center", padx=5, pady=5)

        # Fetch and display the Bundesländer graph
        top_states = fetch_top_states_for_date()
        create_bar_chart(stats_top_right_frame, top_states)

# Create the main tkinter window
root = tk.Tk()
root.title("News Dashboard")

# Configure the grid layout
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Welcome text (top-left)
welcome_frame = tk.Frame(root, borderwidth=2, relief="groove")
welcome_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Add heading
heading_label = tk.Label(welcome_frame, text="German News Dashboard", font=("Arial", 24, "bold"), pady=10)  # Increased font size
heading_label.pack()

welcome_label = tk.Label(welcome_frame, font=("Arial", 16), wraplength=200, justify="center")  # Increased font size
welcome_label.pack(expand=True)

# Start updating the time
update_time()

# Statistics (top-right)
stats_top_right_frame = tk.Frame(root, borderwidth=2, relief="groove")
stats_top_right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# Add buttons to toggle between "Schlagworte" and "Bundesländer"
button_frame = tk.Frame(stats_top_right_frame)
button_frame.pack(anchor="n", pady=5)

schlagworte_button = tk.Button(
    button_frame, text="Schlagworte", font=("Arial", 12), relief="sunken",  # Default selected
    command=lambda: update_top_right_graph("Schlagworte")
)
schlagworte_button.grid(row=0, column=0, padx=10, pady=5)

bundeslaender_button = tk.Button(
    button_frame, text="Bundesländer", font=("Arial", 12), relief="raised",  # Default unselected
    command=lambda: update_top_right_graph("Bundesländer")
)
bundeslaender_button.grid(row=0, column=1, padx=10, pady=5)

# Calculate yesterday's date
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")

# Default graph: Schlagworte
stats_top_right_label = tk.Label(
    stats_top_right_frame, 
    text=f"Diese Themenbereiche waren gestern, am {yesterday_date}, brandaktuell.", 
    font=("Arial", 18, "bold")
)
stats_top_right_label.pack(anchor="w", padx=5, pady=5)

update_top_right_graph("Schlagworte")

# Statistics (bottom-left)
stats_bottom_left_frame = tk.Frame(root, borderwidth=2, relief="groove")
stats_bottom_left_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)  # Moved to column=1

# Fetch and display the line chart for the last 10 days
daily_summary_data = fetch_daily_summary()
create_line_chart(stats_bottom_left_frame, daily_summary_data, "Gesamtanzahl der Artikel (letzte 10 Tage)")

# Statistics (bottom-right)
stats_bottom_right_frame = tk.Frame(root, borderwidth=2, relief="groove")
stats_bottom_right_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)  # Moved to column=0

# Calculate yesterday's date dynamically
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Fetch article counts for yesterday
article_counts = fetch_article_counts_by_state(yesterday_date)

# Create the map for yesterday's date
create_germany_map(stats_bottom_right_frame, "2_hoch.geo.json", article_counts, yesterday_date)

# Run the tkinter main loop
root.mainloop()