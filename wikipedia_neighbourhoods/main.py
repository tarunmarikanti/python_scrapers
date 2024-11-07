import requests
from bs4 import BeautifulSoup
import json

def get_wikipedia_place_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract place name
        place_name_element = soup.find('h1', id='firstHeading')
        place_name = place_name_element.text.strip() if place_name_element else "N/A"

        # Hardcode place type as 'Neighborhood'
        place_type = "Neighborhood"

        # Extract coordinates with checks
        lat_element = soup.find('span', class_='latitude')
        lon_element = soup.find('span', class_='longitude')
        lat = lat_element.text if lat_element else "N/A"
        lon = lon_element.text if lon_element else "N/A"

        # Extract details from the infobox
        infobox = soup.find('table', class_='infobox ib-settlement vcard')
        details = {}
        if infobox:
            for row in infobox.find_all('tr'):
                if row.th and row.td:
                    key = row.th.text.strip()
                    value = row.td.text.strip()
                    if key in ['Country', 'State', 'Region', 'District', 'PIN', 'Parliament constituencies', 'Sasana Sabha constituencies']:
                        details[key] = value

        # Extract images, excluding SVG images
        images = []
        for img in soup.find_all('img'):
            img_src = img.get('src')
            if img_src and not img_src.endswith('.svg'):  # Exclude SVG images
                images.append('https:' + img_src)

        place_data = {
            'placeName': place_name,
            'placeType': place_type,  # Hardcoded
            'coordinates': {'latitude': lat, 'longitude': lon},
            'country': details.get('Country', 'N/A'),
            'state': details.get('State', 'N/A'),
            'region': details.get('Region', 'N/A'),
            'district': details.get('District', 'N/A'),
            'pincode': details.get('PIN', 'N/A'),
            'lokSabhaConstituency': details.get('Parliament constituencies', 'N/A'),
            'vidhanSabhaConstituency': details.get('Sasana Sabha constituencies', 'N/A'),
            'imageUrls': images
        }

        return place_data

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def scrape_neighborhoods_and_save(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all <ul> elements
        uls = soup.find_all('ul')
        base_url = 'https://en.wikipedia.org'

        # Extract regions and neighborhoods
        all_place_data = []
        current_region = 'N/A'

        for element in soup.find_all(['h3', 'ul']):
            if element.name == 'h3':
                current_region = element.text.strip()  # Update the region based on the <h3> tag
            elif element.name == 'ul':
                for li in element.find_all('li'):
                    link = li.find('a', href=True)
                    if link:
                        name = link.text.strip()
                        if name:
                            # Construct URL for each neighborhood
                            neighborhood_url = base_url + link['href']
                            print(f"Processing {name} in region {current_region}...")
                            place_data = get_wikipedia_place_details(neighborhood_url)
                            if place_data and place_data['country'] != 'N/A':
                                # Update region in place_data
                                place_data['region'] = current_region
                                # Append data to the list
                                all_place_data.append(place_data)
        
        # Save all data to a single JSON file
        with open('neighborhoods_data_ss.json', 'w') as json_file:
            json.dump(all_place_data, json_file, indent=4)

        print("All data saved to 'neighborhoods_data_ss.json'.")

    except Exception as e:
        print(f"Error scraping neighborhoods: {e}")

# URL for the list of neighborhoods
url = 'https://en.wikipedia.org/wiki/List_of_neighbourhoods_in_Hyderabad'
scrape_neighborhoods_and_save(url)
