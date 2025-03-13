import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


def format_date(date_str):
    if not date_str:
        return None

    month_mapping = {
        "Ene": "Jan", "Feb": "Feb", "Mar": "Mar", "Abr": "Apr",
        "May": "May", "Jun": "Jun", "Jul": "Jul", "Ago": "Aug",
        "Sep": "Sep", "Oct": "Oct", "Nov": "Nov", "Dic": "Dec"
    }

    try:
        # Case 1: "Dom 06 Abr 00:00hs" -> "YYYY-MM-DD"
        parts = date_str.split()
        if len(parts) == 4 and parts[2] in month_mapping:
            day = parts[1]
            month = month_mapping[parts[2]]
            date_obj = datetime.strptime(f"{day} {month} 2025", "%d %b %Y")  # Assuming 2025, modify as needed
            return date_obj.strftime("%d-%m-%Y")

        # Case 2: "2025-03-25 17:00:00" -> "YYYY-MM-DD"
        elif " " in date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return date_obj.strftime("%d-%m-%Y")

        # Case 3: "2025-03-27" (already correct)
        else:
            return date_str

    except ValueError:
        print(f"Error formatting date: {date_str}")
        return None



url = 'https://arg-sales.com/'
response = requests.get(url)
response.raise_for_status()  

#Parsea html del homepage de antonio bullrich
soup = BeautifulSoup(response.content, 'html.parser')

#Busco seccion de proximos remates
auction_section = soup.find('section', class_='container')

data=[]

from bs4 import BeautifulSoup

data = []


for auction_div in soup.find_all('div', class_='card'):
    a = auction_div.find('h3', class_='h4').find('a') if auction_div.find('h3', class_='h4') else None

    if a:  
        title = a.get_text(strip=True)  
        href = a.get('href')  


        footer = auction_div.find('div', class_='card-footer')

        link_catalogo = url + href

        auction_response = requests.get(link_catalogo)
        auction_response.raise_for_status()
        auction_soup = BeautifulSoup(auction_response.content, 'html.parser')

        catalogo = None  


        pdf = auction_soup.find('a', string="Descargar Catálogo")
        if pdf:
            catalogo = pdf.get('href') 



        if footer:  
            e = footer.find('h6', string=lambda text: text in ("Empieza", "Pre ofertas"))
            t = footer.find('h6', string=lambda text: text in ("Termina", "Presencial"))

            start_raw = e.find_next_sibling('h6').get_text(strip=True) if e else None
            end_raw = t.find_next_sibling('h6').get_text(strip=True) if t else None

            start = format_date(start_raw)
            end = format_date(end_raw)



            data.append({'title': title, 'href': href, 'catalogo':catalogo, 'start': start, 'end': end, 'source':'argsales'})



df = pd.DataFrame(data)


df.to_csv('scraped_data.csv', mode='a', index=False, header=False)  

print(df)