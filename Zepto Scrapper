import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

# API Details
api_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
api_key = "DEMO_KEY"

driver = webdriver.Chrome()

def scrape_items(category_url):
    driver.get(category_url)
    time.sleep(5)

    items_data = []
    scroll_pause_time = 4
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        item_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')
        for item in item_elements:
            # Extracting name, price, and units
            name = item.find_element(By.CSS_SELECTOR, '[data-testid="product-card-name"]').text
            quantity_text = item.find_element(By.CSS_SELECTOR, '[data-testid="product-card-quantity"]').text
            price_text = item.find_element(By.CSS_SELECTOR, '[data-testid="product-card-price"]').text

            quantity_parts = quantity_text.split()
            quantity_value = quantity_parts[0]
            quantity_unit = quantity_parts[1] if len(quantity_parts) > 1 else "N/A"

            # Call the API to get nutrient details
            api_response = requests.get(api_url, params={
                'api_key': api_key,
                'query': name,
                'dataType': 'Survey (FNDDS)'
            })

            food_nutrients = []
            fdcId, foodCode, foodCategory, foodCategoryId = "NA", "NA", "NA", "NA"
            if api_response.status_code == 200:
                data = api_response.json()
                items = data.get("foods", [])
                
                for item in items:
                    description = item.get("description", "")
                    if "raw" in description.lower():
                        fdcId = item.get("fdcId", "NA")
                        foodCode = item.get("foodCode", "NA")
                        foodCategory = item.get("foodCategory", "NA")
                        foodCategoryId = item.get("foodCategoryId", "NA")
                        
                        for nutrient in item.get("foodNutrients", []):
                            nutrient_data = {
                                "nutrientId": nutrient.get("nutrientId", "NA"),
                                "nutrientName": nutrient.get("nutrientName", "NA"),
                                "nutrientNumber": nutrient.get("nutrientNumber", "NA"),
                                "unitName": nutrient.get("unitName", "NA"),
                                "value": nutrient.get("value", "NA"),
                                "rank": nutrient.get("rank", "NA"),
                                "indentLevel": nutrient.get("indentLevel", "NA"),
                                "foodNutrientId": nutrient.get("foodNutrientId", "NA")
                            }
                            food_nutrients.append(nutrient_data)
                        break

            # Append item data
            item_data = {
                "fdcId": fdcId,
                "foodCode": foodCode,
                "foodCategory": foodCategory,
                "foodCategoryId": foodCategoryId,
                "name": name,
                "price": float(price_text.replace("₹", "").strip()),
                "measurement": {
                    "value": quantity_value,
                    "unit": quantity_unit
                },
                "foodNutrients": food_nutrients if food_nutrients else [{"nutrientId": "NA", "nutrientName": "NA"}]
            }
            items_data.append(item_data)

        # Check if reached end
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return items_data

# URLs for vegetables and fruits
vegetable_url = "https://www.zeptonow.com/cn/fruits-vegetables/fresh-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/b4827798-fcb6-4520-ba5b-0f2bd9bd7208"
fruit_url = "https://www.zeptonow.com/cn/fruits-vegetables/fresh-fruits/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/09e63c15-e5f7-4712-9ff8-513250b79942"

# Scrape vegetables and fruits data
vegetables = scrape_items(vegetable_url)
fruits = scrape_items(fruit_url)

# Save both to JSON
final_data = {
    "vegetables": vegetables,
    "fruits": fruits
}

with open("vegetable_and_fruit_data.json", "w") as json_file:
    json.dump(final_data, json_file, indent=4)

print("Task Completed")

driver.quit()
