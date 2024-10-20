import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import urllib.parse

app = FastAPI()

@app.get("/search")
def search_hotwheels(query: str):
    decoded_query = urllib.parse.unquote(query).replace(' ', '_')

    url = f"https://hotwheels.fandom.com/wiki/{decoded_query}?so=search"
    print(url)

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    results = []
    table = soup.find("table", class_="wikitable sortable")

    if table:
        rows = table.find_all("tr")
        headers = [header.text.strip() for header in rows[0].find_all("th")]  # Get headers from the table

        for row in rows[1:]:  # Skip header row
            cols = row.find_all("td")
            if len(cols) == len(headers):
                data = {headers[i]: col.text.strip() for i, col in enumerate(cols)}

                # Add photo URL
                photo_element = cols[-1].find('a', 'image')
                data['Photo'] = photo_element.get('href') if photo_element else None
                # print(data)
                results.append(data)


    return results


@app.get("/scrape/{startyear}/{endyear}")
def fetch_hotwheels(startyear: int, endyear: int):
    all_cars = []

    for year in range(startyear, endyear + 1):
        url = f"https://hotwheels.fandom.com/wiki/List_of_{year}_Hot_Wheels"
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')

        headers = ["ToyID", "Col.#", "ModelName", "Series", "SeriesNumber", "Photo"]
        for table in soup.find_all('table', 'wikitable'):
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) == len(headers):
                    row_data = [col.text.strip() for col in cols[:-1]]

                    # Get series as a string
                    series_cell = cols[headers.index('Series')]
                    row_data[headers.index('Series')] = ', '.join(series_cell.stripped_strings)

                    # Get image link
                    img_link = cols[-1].find('a', 'image')
                    row_data.append(img_link.get('href') if img_link else None)
                    row_data.append(year)

                    if row_data[0]:  # Ensure ToyID is present
                        car = dict(zip(headers + ['Year'], row_data))
                        all_cars.append(car)

    return all_cars
