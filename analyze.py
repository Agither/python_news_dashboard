import json
import requests
from collections import Counter

EXCLUDE_TAGS = [
    "Schleswig-Holstein", "Hamburg", "Niedersachsen", "Bremen", "Nordrhein-Westfalen",
    "Hessen", "Rheinland-Pfalz", "Baden-Württemberg", "Bayern", "Saarland",
    "Berlin", "Brandenburg", "Mecklenburg-Vorpommern", "Sachsen", "Sachsen-Anhalt", "Thüringen",
    "HR", "WDR", "SWR", "rbb", "schnell informiert", "mdr", "NDR", "BR", "SR", "Radio Bremen", 
    "Deutschlandfunk", "Deutschlandfunk Kultur", "Deutschlandfunk Nova", "ARD", "ZDF", 
    "Tagesschau", "heute", "heute journal", "Tagesthemen", "ARD Aktuell", "ZDF heute", 
    "Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Rostock"
]

def fetch_news_from_api(api_url):
    """
    Ruft Daten von der Tagesschau-API ab und gibt die JSON-Daten zurück.
    :param api_url: URL der Tagesschau API.
    :return: JSON-Objekt mit den Nachrichtendaten.
    """
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Löst eine HTTPError aus, wenn der Statuscode fehlerhaft ist
        return response.json()
    except requests.RequestException as e:
        print(f"Fehler beim Abrufen der API-Daten: {e}")
        return None

def extract_news_data(data_source, from_api=False):
    """
    Extrahiert spezifische Informationen aus den ersten 5 Einträgen der Nachrichten. 
    Gibt außerdem die Gesamtanzahl der Artikel zurück.

    :param data_source: Entweder der Pfad zu einer JSON-Datei (für Entwicklungsmodus) oder bereits geladene API-Daten (für Produktionsmodus).
    :param from_api: Ob die Datenquelle eine API ist (True) oder eine lokale Datei (False).
    :return: Tuple: (Liste der extrahierten Nachrichten, Gesamtanzahl der Artikel)
    """
    try:
        if not from_api:  # Lokale Datei lesen
            with open(data_source, 'r') as json_file:
                data = json.load(json_file)
        else:  # Daten direkt aus der API
            data = data_source

        if "news" in data and isinstance(data["news"], list):
            total_articles = len(data["news"])  # Anzahl der gesamten Artikel
            extracted_data = []

            # Begrenzen auf die ersten 5 Einträge
            for news in data["news"][:5]:
                news_info = {
                    "title": news.get("title"),
                    "date": news.get("date"),
                    "tags": news.get("tags"),
                    "regionId": news.get("regionId"),
                    "ressort": news.get("ressort")
                }
                extracted_data.append(news_info)

            return extracted_data, total_articles
        else:
            print("'news' ist nicht vorhanden oder kein Array.")
            return [], 0
    except FileNotFoundError:
        print("Die Datei wurde nicht gefunden. Bitte überprüfen Sie den Pfad.")
        return [], 0
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return [], 0

def analyze_tags_and_region_ids(data_source, from_api=False):
    """
    Analysiert Tags (mindestens 3-mal vorkommend, nach Filterung) und zählt die Bundesländer nach `regionId` (1-16).
    
    :param data_source: JSON-Datei-Pfad (für Entwicklungsmodus) oder API-Daten (für Produktionsmodus).
    :param from_api: Ob die Datenquelle eine API ist (True) oder eine lokale Datei (False).
    :return: Tuple - gefilterte Tags (dict) und Häufigkeiten der Bundesländer (Counter).
    """
    def map_region_id_to_state(region_id):
        region_mapping = {
            1: "Schleswig-Holstein",
            2: "Hamburg",
            3: "Niedersachsen",
            4: "Bremen",
            5: "Nordrhein-Westfalen",
            6: "Hessen",
            7: "Rheinland-Pfalz",
            8: "Baden-Württemberg",
            9: "Bayern",
            10: "Saarland",
            11: "Berlin",
            12: "Brandenburg",
            13: "Mecklenburg-Vorpommern",
            14: "Sachsen",
            15: "Sachsen-Anhalt",
            16: "Thüringen"
        }
        return region_mapping.get(region_id, "Unbekannt")

    try:
        if not from_api:
            with open(data_source, 'r') as json_file:
                data = json.load(json_file)
        else:
            data = data_source

        tags_counter = Counter()
        state_counter = Counter()

        if "news" in data and isinstance(data["news"], list):
            for news in data["news"]:
                # Tags zählen, dabei gefilterte Tags ausschließen
                if "tags" in news and isinstance(news["tags"], list):
                    for tag in news["tags"]:
                        tag_name = tag.get("tag", "")
                        if tag_name not in EXCLUDE_TAGS:  # Ausschluss überprüfen
                            tags_counter[tag_name] += 1

                # Bundesländer zählen basierend auf `regionId`
                if "regionId" in news and isinstance(news["regionId"], int):
                    state = map_region_id_to_state(news["regionId"])
                    if state != "Unbekannt":  # Nimm nur gültige regionIds (1 bis 16)
                        state_counter[state] += 1

        # Filtere Tags mit mind. 3 Vorkommen
        filtered_tags = {tag: count for tag, count in tags_counter.items() if count >= 3}

        return filtered_tags, state_counter
    except Exception as e:
        print(f"Fehler bei der Analyse der Daten: {e}")
        return {}, Counter()