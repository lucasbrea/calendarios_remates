import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

#Get href for bullrich auction lots in csv
csv_file = "scraped_data.csv"

df_href = pd.read_csv(csv_file, header=None, encoding='utf-8', sep=',')

bullrich_df = df_href[df_href.iloc[:, -1].str.strip().str.lower() == "bullrich"]


href_links = bullrich_df.iloc[:, 1].dropna().tolist()

url = 'https://antoniobullrich.com'

# Function to scrape auction data
def scraper_bullrich(url, extension):
    response = requests.get(url + extension)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    auction = soup.find('table', class_='table')

    # Data collection within function
    data = []

    if auction:
        rows = auction.find_all('tr')[1:]
        for row in rows:
            columns = row.find_all('td')
            if len(columns) > 8:
                lote = columns[0].text.strip()
                nombre = columns[1].text.strip()
                hara = columns[5].text.strip()

                #Get lot links for each individual horse to find out birth year 
                a_tag = columns[8].find('a')
                link_lote = url + a_tag['href'] if a_tag and 'href' in a_tag.attrs else None

                

                response_horse = requests.get(link_lote)
                response_horse.raise_for_status()

                soup_caballo = BeautifulSoup(response_horse.content, 'html.parser')

                # Find the correct div
                p_div = soup_caballo.find('div', class_='col-lg-6')

                year = None  # Default value in case it is not found
                if p_div:
                    p_tag = p_div.find('p', string=lambda text: text and "nacida" or "nacido" in text)
                    if p_tag:
                        match = re.search(r'\d{4}', p_tag.get_text(strip=True))
                        if match:
                            year = match.group()  # Extract the matched year

                # Append the cleaned data
            data.append({'Lote': lote, 'Nombre': nombre,'Year': year, 'Hara':hara, 'Link': extension, })


    

    
    return data  # Return collected data

# Collect all scraped data from multiple links
all_data = []


for link in href_links:
    print(f"Scraping: {url+link}")
    scraped_data = scraper_bullrich(url, link)
    all_data.extend(scraped_data)  # Aggregate results

# Save all collected data at once
if all_data:
    df = pd.DataFrame(all_data, columns=['Lote', 'Nombre','Year','Hara', 'Link'])
    df.to_csv('horse_data.csv', mode='a', index=False, header=True)
    print(f"✅ Successfully saved {len(df)} entries to horse_data.csv")

    # Print DataFrame for verification
    print(df)
