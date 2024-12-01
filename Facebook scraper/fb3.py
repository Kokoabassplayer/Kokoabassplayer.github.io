# Don't forget to pip install pandas and facebook_page_scraper
import pandas as pd
from facebook_page_scraper import Facebook_scraper
from datetime import datetime

class GetFacebookPage():
    def __init__(self) -> None:
        pass  # No need to initialize Facebook_scraper here

    def scrap_to_csv(self, page_name, posts_count):
        # Get the current date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Dynamically name the file based on the page_name, current date, and posts_count
        file_name = f"FB_{page_name}_{posts_count}_latest_posts_{current_date}"
        
        # Initialize Facebook_scraper when you actually need it
        self.F = Facebook_scraper(page_name, posts_count, browser="firefox", proxy="IP:PORT", timeout=600, headless=True)
        
        # Save the scraped data to a CSV file
        self.F.scrap_to_csv(file_name)  # Assuming scrap_to_csv saves the file

    def some_other_functionality(self):
        # Implement other functionalities similar to the Instagram scraper
        pass

if __name__ == "__main__":
    cls = GetFacebookPage()
    
    # Example usage: Scraping posts to CSV
    cls.scrap_to_csv(page_name="ondemandacademy", posts_count=100)