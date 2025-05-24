import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask, jsonify


# Ligi i drużyny podhalańskie
LIGI = {
    "III Liga (gr. IV)": {
        "url": "http://www.90minut.pl/liga/1/liga13559.html",
        "filtruj": True,
        "druzyny": ["Podhale Nowy Targ"]
    },
    "IV Liga Małopolska": {
        "url": "http://www.90minut.pl/liga/1/liga13624.html",
        "filtruj": True,
        "druzyny": ["Watra Białka Tatrzańska", "Lubań Maniowy"]
    },
    "V Liga Małopolska Wschód": {
        "url": "http://www.90minut.pl/liga/1/liga13789.html",
        "filtruj": True,
        "druzyny": ["LKS Szaflary", "Jordan Jordanów"]
    },
    "Klasa Okręgowa (Limanowa - Podhale)": {
        "url": "http://www.90minut.pl/liga/1/liga13666.html",
        "filtruj": True,
        "druzyny": [
            "Wisła Czarny Dunajec", "Orawa Jabłonka", "Huragan Waksmund",
            "Lubań Tylmanowa", "Orkan Raba Wyżna", "Zawrat Bukowina Tatrzańska",
            "Babia Góra Lipnica Wielka", "Wierchy Rabka Zdrój", "Wiatr Ludźmierz"
        ]
    },
    "A Klasa Podhale": {
        "url": "http://www.90minut.pl/liga/1/liga13709.html",
        "filtruj": False
    },    
    "B Klasa Podhale gr. 1": {
        "url": "http://www.90minut.pl/liga/1/liga13924.html",
        "filtruj": False
    },
    "B Klasa Podhale gr. 2": {
        "url": "http://www.90minut.pl/liga/1/liga13925.html",
        "filtruj": False
    },    

}

# Mapowanie nazw miesięcy na numery
miesiace = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6,
    "lipca": 7, "sierpnia": 8, "września": 9, "października": 10, "listopada": 11, "grudnia": 12
}

# Tydzień: poniedziałek-niedziela
today = datetime.today()
start_week = today - timedelta(days=today.weekday())
end_week = start_week + timedelta(days=6)

# Lista meczów
wszystkie_mecze = []

# Mapping PL dni tygodnia 
dni_tygodnia = {
    0: "Poniedziałek", 1: "Wtorek", 2: "Środa", 3: "Czwartek",
    4: "Piątek", 5: "Sobota", 6: "Niedziela"
}

# Przetwarzanie
for nazwa_ligi, dane in LIGI.items():
    print(f"\n Przetwarzam: {nazwa_ligi}")
    response = requests.get(dane["url"])
    response.encoding = 'ISO-8859-2'
    soup = BeautifulSoup(response.text, "html.parser")

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            # Domyślnie: szukamy daty w ostatniej kolumnie
            data_text = cols[-1].get_text(strip=True)
            data_attr = row.get("data-date")
            data_meczu = None

            # Próba parsowania z atrybutu HTML
            if data_attr:
                try:
                    data_meczu = datetime.strptime(data_attr, "%Y-%m-%d")
                except:
                    pass

            # Próba parsowania z tekstu
            if not data_meczu:
                for miesiac_txt, miesiac_num in miesiace.items():
                    if miesiac_txt in data_text:
                        try:
                            dzien_str, godzina = data_text.split(',')
                            dzien = int(dzien_str.strip().split()[0])
                            godziny = list(map(int, godzina.strip().split(':')))
                            data_meczu = datetime(today.year, miesiac_num, dzien, *godziny)
                            break
                        except:
                            continue

            if not data_meczu or not (start_week.date() <= data_meczu.date() <= end_week.date()):
                continue

            # Drużyny
            gospodarz = cols[0].get_text(strip=True)
            gosc = cols[2].get_text(strip=True)

            # Filtruj, jeśli trzeba
            if dane.get("filtruj"):
                if not any(team in [gospodarz, gosc] for team in dane["druzyny"]):
                    continue

            # Dodaj do listy
            dzien_tygodnia = dni_tygodnia[data_meczu.weekday()]
            mecz_str = f"{nazwa_ligi}: {gospodarz} vs {gosc} – {dzien_tygodnia} – {data_meczu.strftime('%d.%m.%Y %H:%M')}"
            if mecz_str not in wszystkie_mecze:
                wszystkie_mecze.append(mecz_str)

# Wynik
app = Flask(__name__)

@app.route('/api/mecze', methods=['GET'])
def get_mecze():
    return jsonify({"mecze": wszystkie_mecze})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)