from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--allow-running-insecure-content')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

driver.get("https://www.nike.com")

wait = WebDriverWait(driver, 20)
search_icon = None

try:
    search_icon = wait.until(EC.element_to_be_clickable((By.ID, "nav-search-icon")))
except TimeoutException:
    print("Icono de búsqueda no encontrado usando ID.")

if search_icon:
    search_icon.click()
    
    try:
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "gn-search-input")))
        search_box.click()
        search_box.send_keys("Nike Air Force 1")
        search_box.send_keys(Keys.ENTER)
    except TimeoutException:
        print("Campo de búsqueda no encontrado usando ID.")

    products_wrapper = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-grid")))

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    time.sleep(5)

    products = products_wrapper.find_elements(By.CSS_SELECTOR, "div.product-card__body")

    product_names = []
    product_prices = []

    for product in products:
        product_name = product.find_element(By.CSS_SELECTOR, "div.product-card__title").text
        product_names.append(product_name)
        
        try:
            product_price = product.find_element(By.CSS_SELECTOR, "div.product-price").text
        except:
            product_price = "N/A"
        product_prices.append(product_price)

    df = pd.DataFrame({
        'Tenis': product_names,
        'Precio': product_prices
    })

    df.to_excel('nike_air_force_1.xlsx', index=False)
    df.to_csv('nike_air_force_1.csv', index=False)
    print("Datos guardados")
else:
    print("No se pudo encontrar el icono de búsqueda.")

driver.quit()
