from web_scraper import WebScraper

if __name__ == "__main__":
    scraper = WebScraper(config_file='config2.json')
    scraper.setup_driver()
    scraper.execute_actions()
    scraper.quit()
