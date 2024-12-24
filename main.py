from scraper import MedicineScraper
from save import DataSaver
from dotenv import load_dotenv
import os
import logging
from typing import List, Dict

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    # Setup
    load_dotenv()
    logger = setup_logging()
    base_url = os.getenv('BASE_URL', 'https://medex.com.bd/generics?page=')
    data_saver = DataSaver()
    
    try:
        # Initialize scraper
        scraper = MedicineScraper(base_url)
        
        # Get initial counts
        initial_counts = data_saver.get_saved_count()
        logger.info(f"Initial data counts - Raw: {initial_counts['raw_count']}, Processed: {initial_counts['processed_count']}")
        
        # Scrape medicine data (processing and saving happens incrementally in the scraper)
        logger.info("Starting medicine data scraping...")
        scraper.scrape_medicine_data(start_page=1, end_page=1)
        
        # Get final counts
        final_counts = data_saver.get_saved_count()
        logger.info(f"Final data counts - Raw: {final_counts['raw_count']}, Processed: {final_counts['processed_count']}")
        logger.info(f"New items added - Raw: {final_counts['raw_count'] - initial_counts['raw_count']}, " + 
                   f"Processed: {final_counts['processed_count'] - initial_counts['processed_count']}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
