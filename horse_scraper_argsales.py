from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import re

csv_file = "scraped_data.csv"  

df_href = pd.read_csv(csv_file, header=None)  

argsales_df = df_href[df_href.iloc[:, -1] == "argsales"]  # Selects only rows with "argsales"

href_links = argsales_df[1].dropna().tolist()

print(href_links)
data = []


def scraper_caballos(url, extension):

    response = requests.get(url+extension)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    for auction_div in soup.find_all('div', class_='card-body'):

        p = auction_div.find('p', class_='mb-0 fs-sm')

        lot_number = None
        year = None

        if p:

            lot_number = p.get_text(separator=" / ", strip=True).split(" / ")[0].replace("Lote ", "").strip()
            
    
            small_tag = p.find('small')
            year = small_tag.get_text(strip=True).replace("Productos ", "") if small_tag else None

        name = auction_div.find('h4', class_='mb-3').get_text(strip=True) if auction_div.find('h4', class_='mb-3') else None

        p_hara= auction_div.find('p', string=lambda text: text and "|" in text)


        hara = None
        if p_hara:
            text_parts = p_hara.get_text(strip=True).split('|') 
            hara = text_parts[-1].strip()  
        else:None

        data.append({'lote': lot_number, 'name': name, 'year': year, 'hara': hara, 'href':extension})

url = 'https://arg-sales.com'


for link in href_links:
    scraper_caballos(url, link)

df = pd.DataFrame(data)


df.to_csv('horse_data.csv', mode='a', index=False, header=True)  


