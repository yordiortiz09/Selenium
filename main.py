import json
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Leer el archivo JSON
with open('config.json', 'r') as file:
    config = json.load(file)

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--allow-running-insecure-content')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 20)

def scrape_site(site):
    driver.get(site["url"])

    try:
        search_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, site["search_icon"]["value"])))
        search_icon.click()
    except TimeoutException:
        print(f"Icono de búsqueda no encontrado en {site['name']}.")

    try:
        search_box = wait.until(EC.element_to_be_clickable((By.ID, site["search_box"]["value"])))
        search_box.click()
        search_box.send_keys(site["search_term"])
        search_box.send_keys(Keys.ENTER)
    except TimeoutException:
        print(f"Campo de búsqueda no encontrado en {site['name']}.")

    try:
        products_wrapper = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, site["products_wrapper"]["value"])))
    except TimeoutException:
        print(f"Contenedor de productos no encontrado en {site['name']}.")
        return

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    time.sleep(5)

    products = products_wrapper.find_elements(By.CSS_SELECTOR, site["product_name"]["value"])

    product_names = []
    product_prices = []

    for product in products:
        product_name = product.text
        product_names.append(product_name)

        try:
            product_price = product.find_element(By.CSS_SELECTOR, site["product_price"]["value"]).text
        except:
            product_price = "N/A"
        product_prices.append(product_price)

    df = pd.DataFrame({
        'Producto': product_names,
        'Precio': product_prices
    })

    filename = site["name"].replace(" ", "_").lower()
    df.to_excel(f'{filename}.xlsx', index=False)
    df.to_csv(f'{filename}.csv', index=False)
    print(f"Datos guardados para {site['name']}.")

for site in config["sites"]:
    scrape_site(site)

driver.quit()
