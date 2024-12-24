import json
import os
import logging
from typing import Dict, List
from dotenv import load_dotenv

class DataSaver:
    def __init__(self):
        load_dotenv()
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.raw_data_file = 'raw_medicine_data.json'
        self.processed_data_file = 'processed_medicine_data.json'

    def _load_existing_data(self, filename: str) -> List[Dict]:
        """Load existing data from file if it exists"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error loading existing data from {filename}: {str(e)}")
            return []

    def _is_duplicate(self, new_data: Dict, existing_data: List[Dict]) -> bool:
        """Check if medicine data already exists based on key attributes"""
        for existing in existing_data:
            if (
                existing.get('product_name') == new_data.get('product_name') and
                existing.get('generic_name') == new_data.get('generic_name') and
                existing.get('manufacturer') == new_data.get('manufacturer') and
                existing.get('strength') == new_data.get('strength') and
                existing.get('price_info', {}).get('unit_price') == new_data.get('price_info', {}).get('unit_price')
            ):
                return True
        return False

    def save_raw_data(self, data: Dict) -> bool:
        """Save raw medicine data with duplicate checking"""
        try:
            existing_data = self._load_existing_data(self.raw_data_file)
            
            if self._is_duplicate(data, existing_data):
                self.logger.debug(f"Skipping duplicate medicine: {data.get('product_name')}")
                return False
                
            existing_data.append(data)
            
            with open(self.raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
            self.logger.debug(f"Saved raw data for medicine: {data.get('product_name')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving raw data: {str(e)}")
            return False

    def save_processed_data(self, data: Dict) -> bool:
        """Save AI-processed medicine data with duplicate checking"""
        try:
            existing_data = self._load_existing_data(self.processed_data_file)
            
            if self._is_duplicate(data, existing_data):
                self.logger.debug(f"Skipping duplicate processed medicine: {data.get('product_name')}")
                return False
                
            existing_data.append(data)
            
            with open(self.processed_data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
            self.logger.debug(f"Saved processed data for medicine: {data.get('product_name')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving processed data: {str(e)}")
            return False

    def get_saved_count(self) -> Dict[str, int]:
        """Get count of saved raw and processed medicines"""
        raw_count = len(self._load_existing_data(self.raw_data_file))
        processed_count = len(self._load_existing_data(self.processed_data_file))
        return {
            'raw_count': raw_count,
            'processed_count': processed_count
        }
