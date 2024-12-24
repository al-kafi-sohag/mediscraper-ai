import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import time
from dotenv import load_dotenv
import os
from save import DataSaver
from ai_processor import MedicineAIProcessor
import random

class MedicineScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        load_dotenv()
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.data_saver = DataSaver()
        self.ai_processor = MedicineAIProcessor()
        
        # Common browser user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Load sleep timers from environment
        self.page_sleep = float(os.getenv('PAGE_SLEEP_TIME', '1.0'))
        self.product_sleep = float(os.getenv('PRODUCT_SLEEP_TIME', '0.5'))
        self.logger.debug(f"Sleep timers - Page: {self.page_sleep}s, Product: {self.product_sleep}s")

    def _get_headers(self) -> Dict:
        """Generate random headers for requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def scrape_medicine_data(self, start_page: int = 1, end_page: int = 1) -> List[Dict]:
        """Scrape medicine data from multiple pages"""
        medicine_data = []
        for page in range(start_page, end_page + 1):
            try:
                page_url = self.base_url + str(page)
                response = requests.get(page_url, headers=self._get_headers())
                response.raise_for_status()
                page_soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all generic medicine links
                generic_links = page_soup.find_all('a', class_='hoverable-block darker')
                
                for generic_link in generic_links:
                    products = self._process_generic_page(generic_link['href'])
                    medicine_data.extend(products)
                    
                self.logger.debug(f"Sleeping for {self.page_sleep}s after page {page}")
                time.sleep(self.page_sleep)  # Rate limiting between pages
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {str(e)}")
                continue
                
        return medicine_data

    def _process_generic_page(self, generic_url: str) -> List[Dict]:
        """Process a generic medicine page and extract all products"""
        products = []
        try:
            response = requests.get(generic_url, headers=self._get_headers())
            response.raise_for_status()
            generic_soup = BeautifulSoup(response.content, 'html.parser')
            
            product_links = generic_soup.find_all('a', class_='hoverable-block')
            
            for product_link in product_links:
                # Extract and save product data incrementally
                product_data = self._extract_product_details(product_link['href'])
                if product_data:
                    # Save raw data
                    if self.data_saver.save_raw_data(product_data):
                        # Process with AI and save if raw data was saved
                        processed_data = self.ai_processor.process_medicine(product_data)
                        self.data_saver.save_processed_data(processed_data)
                        products.append(processed_data)
                    
                self.logger.debug(f"Sleeping for {self.product_sleep}s after product {product_data.get('product_name', 'unknown')}")
                time.sleep(self.product_sleep)  # Rate limiting between products
                
        except Exception as e:
            self.logger.error(f"Error processing generic page {generic_url}: {str(e)}")
            
        return products

    def _extract_product_details(self, product_url: str) -> Optional[Dict]:
        """Extract detailed information for a specific product"""
        try:
            response = requests.get(product_url, headers=self._get_headers())
            response.raise_for_status()
            product_soup = BeautifulSoup(response.content, 'html.parser')
            
            product_data = {
                'product_name': self._clean_text(product_soup.find('h1', class_='page-heading-1-l brand')),
                'product_url': product_url,
                'generic_name': self._clean_text(product_soup.find('div', title='Generic Name')),
                'manufacturer': self._clean_text(product_soup.find('div', title='Manufactured by')),
                'strength': self._clean_text(product_soup.find('div', title='Strength')),
                'description': self._clean_text(product_soup.find('div', class_='product-description')),
                'details': self._clean_text(product_soup.find('div', class_='ac-body')),
                'price_info': self._extract_price_info(product_soup),
                'image_url': self._extract_image_url(product_soup)
            }
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Error extracting product details from {product_url}: {str(e)}")
            return None

    def _extract_price_info(self, product_soup: BeautifulSoup) -> Dict:
        """Extract price information from the product page"""
        price_info = {
            'unit_price': '',
            'pack_name': '',
            'pack_price': '',
            'strip_name': '',
            'strip_price': ''
        }
        
        try:
            price_div = product_soup.find('div', class_='package-container mt-5 mb-5')
            if price_div:
                # Extract Unit Price
                spans = price_div.find_all('span')
                if len(spans) > 1:
                    price_info['unit_price'] = spans[1].text.strip().replace('৳', '').strip()

                # Extract Pack Information
                pack_info = price_div.find('span', class_='pack-size-info')
                if pack_info:
                    pack_text = pack_info.text.strip().replace('(', '').replace(')', '')
                    pack_name, pack_price = pack_text.split(': ')
                    price_info['pack_name'] = pack_name + "'s pack"
                    price_info['pack_price'] = pack_price.replace('৳', '').strip()

                    # Extract Strip Information
                    strip_div = price_div.find('div')
                    if strip_div and len(strip_div.find_all('span')) > 1:
                        price_info['strip_name'] = pack_name.split(' ')[0] + "'s strip"
                        price_info['strip_price'] = strip_div.find_all('span')[1].text.strip().replace('৳', '').strip()
                        
        except Exception as e:
            self.logger.error(f"Error extracting price information: {str(e)}")
            
        return price_info

    def _extract_image_url(self, product_soup: BeautifulSoup) -> str:
        """Extract product image URL"""
        try:
            product_image_tag = product_soup.find('img', class_='img-defer')
            return product_image_tag['data-src'] if product_image_tag else ''
        except Exception:
            return ''

    def _clean_text(self, element) -> str:
        """Clean and normalize text from BeautifulSoup element"""
        if element:
            return ' '.join(element.text.strip().split())
        return ''
