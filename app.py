# app.py
from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/mecze')
def mecze():
    # Tydzień: poniedziałek - niedziela
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    url = 'https://www.laczynaspilka.pl/rozgrywki?season=4be7b40c-84ff-4e5a-96e5-875d7f13483a&leagueGroup=e978c8e5-d903-4a89-b6b5-8d5da6c567ee&leagueId=337bb869-0b42-484f-8eca-0c8842a13ec9&subLeague=63d04023-727a-4c0c-a8c6-4154fe1104b7&enumType=ZpnAndLeagueAndPlay&group=780f4e03-5178-4538-9c0f-da491aee362c&voivodeship=143a5a9a-5aa8-4186-ac19-d39e1d198ddb&isAdvanceMode=false&genderType=Male'
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Znajdź mecze — struktura może się zmienić, więc trzeba przetestować na żywo
    matches = []
    for div in soup.select('.match-group__match'):  # <- może wymagać dostosowania
        try:
            date_str = div.select_one('.match-group__match-date').text.strip()
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            if start_of_week <= date_obj <= end_of_week:
                home = div.select_one('.match-group__team--home').text.strip()
                away = div.select_one('.match-group__team--away').text.strip()
                matches.append({
                    'data': date_obj.strftime('%Y-%m-%d'),
                    'gospodarz': home,
                    'gosc': away
                })
        except Exception:
            continue

    return jsonify(matches)

if __name__ == '__main__':
    app.run(debug=True)
