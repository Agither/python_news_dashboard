from analyze import fetch_news_from_api, extract_news_data, analyze_tags_and_region_ids
from database_helper import initialize_database, update_tags_in_db, update_states_in_db, update_article_count, get_current_date
import time

API_URL = "https://www.tagesschau.de/api2u/news"

def main(develop_mode=False):
    if develop_mode:
        print("Entwicklungsmodus aktiviert (develop_mode = True).")
        file_path = 'test-data.json' # Nutze die JSON-Datei als Datenquelle
        filtered_tags, state_counter = analyze_tags_and_region_ids(file_path, from_api=False)
        extracted_news, total_articles = extract_news_data(file_path, from_api=False)

        print(f"Gesamtanzahl der Artikel: {total_articles}")
        print("\nDie letzten 5 Meldungen des Tages:")
        for news in extracted_news:
            print(f"- {news['title']}")

        print("\nTags (mindestens 3-mal vorkommend, absteigend sortiert):")
        if filtered_tags:
            for tag, count in sorted(filtered_tags.items(), key=lambda x: x[1], reverse=True):
                print(f"- {tag}: {count}")
        else:
            print("Keine Tags verfügbar, die mindestens 3-mal vorkommen.")

        print("\nBundesländer (absteigend nach Häufigkeit):")
        if state_counter:
            for state, count in state_counter.most_common():
                print(f"- {state}: {count}")
        else:
            print("Keine Bundesländer verfügbar.")

    else:
        print("Produktionsmodus aktiviert (develop_mode = False).")
        initialize_database()

        while True:
            current_date = get_current_date()

            # API-Daten abrufen
            api_data = fetch_news_from_api(API_URL)
            if api_data is None:
                print("Keine Daten von der API verfügbar. Versuche es in 60 Sekunden erneut...")
                time.sleep(60)
                continue
            
            filtered_tags, state_counter = analyze_tags_and_region_ids(api_data, from_api=True)
            _, total_articles = extract_news_data(api_data, from_api=True)

            # Ergebnisse in die Datenbank speichern
            update_tags_in_db(filtered_tags, current_date)
            update_states_in_db(state_counter, current_date)
            update_article_count(current_date, total_articles)

            print(f"Ergebnisse für {current_date} gespeichert: {total_articles} Artikel.")
            print("Programm wird in 24 Stunden erneut ausgeführt...")
            time.sleep(86400)  # 24 Stunden warten

if __name__ == "__main__":
    main()
