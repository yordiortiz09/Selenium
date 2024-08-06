import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from actions import handle_click, handle_extract, handle_scroll, handle_send_keys, handle_wait

class WebScraper:
    def __init__(self, config_file):
        self.config_file = config_file
        self.driver = None
        self.wait = None
        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            return json.load(file)

    def setup_driver(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=Options())
        self.wait = WebDriverWait(self.driver, 20)

    def execute_actions(self):
        for site in self.config['sites']:
            self.driver.get(site['url'])
            for action in site['actions']:
                action_type = action['type']
                if action_type == 'click':
                    handle_click(self.driver, self.wait, action, site['name'])
                elif action_type == 'wait_for_element':
                    handle_wait(self.driver, self.wait, action, site['name'])
                elif action_type == 'send_keys':
                    handle_send_keys(self.driver, self.wait, action, site['name'])
                elif action_type == 'scroll':
                    handle_scroll(self.driver, self.wait, action, site['name'])
                elif action_type == 'extract':
                    handle_extract(self.driver, self.wait, action, site['name'])

    def quit(self):
        if self.driver:
            self.driver.quit()
