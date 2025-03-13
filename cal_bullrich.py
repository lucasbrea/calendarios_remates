import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

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
    

url = 'https://antoniobullrich.com/'
response = requests.get(url)
response.raise_for_status()  


soup = BeautifulSoup(response.content, 'html.parser')

auction_section = soup.find('section', class_='proximos')


auctions = []

if auction_section:

    for auction_div in auction_section.find_all('div', class_='bullrich-item'):
        title = auction_div.find('h3').get_text(strip=True) 

        date_p = auction_div.find('p')  


        botones = auction_div.find_next_sibling('div', class_="bullrich-item-buttons") 

        catalogo= None
        href = None
        if botones:
            a = botones.find('a', string="Ver Remate")

            if a:
                href = a.get('href')

            cat_a = botones.find('a', string="Descargar Catálogo")
            if cat_a:  
                catalogo = cat_a.get('href')
        if date_p:
            date_str = date_p.get_text(strip=True).strip()
            date = format_date(date_str)

        auctions.append({'title': title,'href':href, 'catalogo':catalogo,  'start': date, 'end':date,  'source':"Bullrich" })


df = pd.DataFrame(auctions)

df.to_csv('scraped_data.csv', mode='a', index=False, header=False)  

print(df)