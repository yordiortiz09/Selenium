import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

def handle_click(driver, wait, action, site_name):
    try:
        by = action['selector']['by'].upper().replace(" ", "_")
        element = wait.until(EC.element_to_be_clickable((getattr(By, by), action['selector']['value'])))
        element.click()
    except Exception as e:
        print(f"Error clicking on {site_name}: {e}")

def handle_extract(driver, wait, action, site_name):
    try:
        time.sleep(5)
        rows = driver.find_elements(By.CSS_SELECTOR, action['selector']['value'])
        print(f"Total rows found in {site_name}: {len(rows)}")

        extracted_data = []
        for row in rows:
            data = {}
            for field in action['fields']:
                try:
                    element = row.find_element(by=getattr(By, field['selector']['by'].upper()), value=field['selector']['value'])
                    data[field['name']] = element.text.strip() if field['name'] != 'link' else element.get_attribute('href').strip()
                except NoSuchElementException:
                    data[field['name']] = ''
            if any(data.values()):
                extracted_data.append(data)
                print(f"Extracted data: {data}")

        save_to_files(extracted_data, site_name)
    except Exception as e:
        print(f"Error extracting data in {site_name}: {e}")

def handle_scroll(driver, wait, action, site_name):
    try:
        settings = action['settings']
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(settings['repetitions']):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(settings['wait_time'])
            new_height = driver.execute_script("return document.body.scrollHeight")
            print(f"Scrolling {i+1}/{settings['repetitions']}: last_height = {last_height}, new_height = {new_height}")
            if new_height == last_height:
                break
            last_height = new_height
            time.sleep(3)
            for j in range(10):
                driver.execute_script("window.scrollBy(0, window.innerHeight / 10);")
                time.sleep(1)
        time.sleep(5)
    except Exception as e:
        print(f"Error scrolling in {site_name}: {e}")

def handle_send_keys(driver, wait, action, site_name):
    try:
        element = wait.until(EC.presence_of_element_located((getattr(By, action['selector']['by'].upper()), action['selector']['value'])))
        element.send_keys(action['value'])
        element.send_keys(Keys.ENTER)
    except Exception as e:
        print(f"Error sending keys in {site_name}: {e}")

def handle_wait(driver, wait, action, site_name):
    try:
        if action['selector']['by'] == 'seconds':
            time.sleep(action['selector']['value'])
        else:
            wait.until(EC.presence_of_element_located((getattr(By, action['selector']['by'].upper()), action['selector']['value'])))
    except Exception as e:
        print(f"Error waiting for element in {site_name}: {e}")

def save_to_files(data, description):
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Crear el DataFrame
    df = pd.DataFrame(data)

    # Renombrar las columnas a español
    df.rename(columns={
        'name': 'Nombre',
        'price': 'Precio'
    }, inplace=True)

    excel_file = os.path.join(output_dir, f'{description}.xlsx')
    csv_file = os.path.join(output_dir, f'{description}.csv')
    excel_file = excel_file.replace(" ", "_")
    csv_file = csv_file.replace(" ", "_")

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']

        (max_row, max_col) = df.shape
        cell_range = f'A1:{chr(65 + max_col - 1)}{max_row + 1}'

        worksheet.add_table(cell_range, {'columns': [{'header': col} for col in df.columns]})

    df.to_csv(csv_file, index=False)

    print(f'Extracted {len(data)} items.')
    print(f'Data saved in "{excel_file}" and "{csv_file}".')
