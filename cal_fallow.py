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

url = 'https://www.fallowremates.com'

response = requests.get(url)

response.raise_for_status()

soup=BeautifulSoup(response.content, 'html.parser')

data = []

for card in soup.find_all('div', class_='card-body'):

    #Titulo
    h1_element = card.find('h1', class_='text-center')  

    #Href
    a = card.find('a')

    #Fehca comienzo
    fecha_inicio = card.find('p', string=lambda text: text and text.strip() == "EMPIEZA")

    #Fecha finalizacion
    fecha_finalizacion = card.find('p', string=lambda text: text and text.strip() == "TERMINA")

    #Catalogo
    pdf  =  card.find('a', string='Descargar Catálogo')

    if pdf:
        catalogo = pdf.get('href')
    else: None


    if fecha_inicio:
        start_raw = fecha_inicio.find_next_sibling('p').get_text(strip=True) if fecha_inicio.find_next_sibling('p') else None
        start = format_date(start_raw)

    if fecha_finalizacion:
         end_raw= fecha_finalizacion.find_next_sibling('p').get_text(strip=True) if fecha_finalizacion.find_next_sibling('p') else None
         end = format_date(end_raw)

    if a:
        href = a.get('href')
    else: None
    
    if h1_element:
        title = h1_element.get_text(strip=True) 
    else: None 



       
    data.append({'title': title, 'href': href, 'catalogo':catalogo, 'start':start, 'end':end, 'source':'fallowremates'})


df  = pd.DataFrame(data)

df.to_csv('scraped_data.csv', mode='a', index=False, header=False)  

print(df)






