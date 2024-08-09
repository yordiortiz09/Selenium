import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup 
from selenium.webdriver.support.ui import Select
import unicodedata


def handle_click(driver, wait, action, site_name):
    try:
        by = action['selector']['by'].upper().replace(" ", "_")
        element = wait.until(EC.element_to_be_clickable((getattr(By, by), action['selector']['value'])))
        element.click()
    except Exception as e:
        print(f"Error clicking on {site_name}: {e}")


def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def handle_select_option(driver, wait, action, site_name):
    try:
        element = wait.until(EC.presence_of_element_located((getattr(By, action['selector']['by'].upper()), action['selector']['value'])))
        select = Select(element)

        normalized_value = normalize_text("Ingeniería Electrónica")

        for option in select.options:
            if normalize_text(option.text) == normalized_value:
                select.select_by_visible_text(option.text)
                break

        print(f"Option 'Ingeniería Electrónica' selected in {site_name}.")
    except Exception as e:
        print(f"Error selecting option in {site_name}: {e}")

def handle_extract(driver, wait, action, site_name):
    try:
        time.sleep(10) 
        rows = driver.find_elements(By.CSS_SELECTOR, action['selector']['value'])
        print(f"Total rows found in {site_name}: {len(rows)}")

        extracted_data = []
        for index, row in enumerate(rows):
            data = {}
            print(f"Processing row {index + 1}/{len(rows)}")
            for field in action['fields']:
                try:
                    element = row.find_element(by=getattr(By, field['selector']['by'].upper()), value=field['selector']['value'])
                    if element:
                        print(f"Element found for field '{field['name']}': {element.get_attribute('outerHTML')}")
                        text = element.get_attribute('innerText').strip()
                        text = ' '.join(text.split())

                        if text:
                            data[field['name']] = text
                        else:
                            print(f"No meaningful text found in field '{field['name']}', setting as empty.")
                            data[field['name']] = ''
                    else:
                        print(f"Field '{field['name']}' not found, setting as empty.")
                        data[field['name']] = ''
                except NoSuchElementException:
                    print(f"Field '{field['name']}' not found in row, setting as empty.")
                    data[field['name']] = ''
                except Exception as e:
                    print(f"Error extracting '{field['name']}' in {site_name}: {e}")
                    data[field['name']] = ''
            if any(data.values()):
                extracted_data.append(data)
                print(f"Extracted data for row {index + 1}: {data}")
            else:
                print(f"No data found in row {index + 1}")
        
        if extracted_data:
            save_to_files(extracted_data, site_name)
        else:
            print("No data extracted, skipping file save.")
    except Exception as e:
        print(f"Error extracting data in {site_name}: {e}")



def handle_extract_table(driver, wait, action, site_name):
    try:
        time.sleep(5)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.select_one(action['selector']['value'])
        rows = table.find_all('tr')

        extracted_data = []
        for row in rows[1:]:
            cells = row.find_all('td')
            if cells:
                data = {}
                for field in action['fields']:
                    try:
                        cell = cells[action['fields'].index(field)]
                        data[field['name']] = cell.get_text(strip=True)
                    except IndexError:
                        data[field['name']] = ''
                if any(data.values()):
                    extracted_data.append(data)
                    print(f"Extracted data: {data}")

        save_to_files(extracted_data, site_name)
    except Exception as e:
        print(f"Error extracting table data in {site_name}: {e}")

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
    
    df = pd.DataFrame(data)

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

        worksheet.add_table(cell_range, {
            'columns': [{'header': col} for col in df.columns],
            'style': 'Table Style Medium 2',
            'autofilter': False
        })

        for i, col in enumerate(df.columns):
            max_width = df[col].astype(str).map(len).max()
            worksheet.set_column(i, i, max(max_width, len(col)) + 2)

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D0E0E3',  
            'font_color': 'black',
            'border': 1})

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

    df.to_csv(csv_file, index=False)

    print(f'Extracted {len(data)} items.')
    print(f'Data saved in "{excel_file}" and "{csv_file}".')

