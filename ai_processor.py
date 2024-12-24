import google.generativeai as genai
from typing import Dict, List, Optional
import logging
import os
from dotenv import load_dotenv
import time
import json
import re

def extract_json_from_text(text: str) -> str:
    """Extract JSON content from text that may be wrapped in markdown code blocks."""
    # Try to find JSON content within markdown code blocks
    json_match = re.search(r'```(?:json)?\s*({\s*.*?\s*})\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # If no markdown blocks found, try to find raw JSON
    json_match = re.search(r'({\s*.*?\s*})', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # If no JSON-like content found, return the original text
    return text

class MedicineAIProcessor:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv('OPENAI_API_KEY'))
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.ai_sleep = float(os.getenv('AI_SLEEP_TIME', '1.0'))
        self.model = genai.GenerativeModel(os.getenv('OPENAI_MODEL', 'gemini-1.0-pro'))
        self.logger.debug(f"AI Configuration - Model: {self.model}, Sleep timer: {self.ai_sleep}s")

    def generate_user_tips(self, medicine_data: Dict) -> List[str]:
        """Generate user-friendly tips based on medicine data"""
        try:
            prompt = f"""
            You are an expert in providing user-friendly and actionable insights based on detailed information. Your task is to extract one important user tip from the given medicine information and present it clearly and concisely.

            Medicine Information:
            - Product Name: {medicine_data['product_name']}
            - Generic Name: {medicine_data['generic_name']}
            - Description: {medicine_data['description']}
            - Details: {medicine_data['details']}

            Your response must:
            1. Be concise and under 30 words.
            2. Focus on practical, actionable advice for users based on the provided information.
            3. Avoid repeating the provided details verbatim unless essential for clarity.
            4. Be formatted strictly as JSON. Do not include any additional text, explanations, or comments outside of the JSON structure.

            Output: Provide the user tip in the following JSON format:
            {{
            "status": 1,
            "message": "Successfully generated user tip",
            "data": {{
                "user_tip": "Example user tip here"
            }}
            }}

            If the information provided is insufficient to generate a tip, return:
            {{
            "status": 0,
            "message": "Insufficient information to generate a user tip",
            "data": null
            }}

            Strictly adhere to the JSON format and ensure no additional text or explanations are included outside of the JSON structure.
            """

            
            response = self.model.generate_content(prompt)
            try:
                # Extract JSON content from potential markdown code block
                json_text = extract_json_from_text(response.text)
                json_data = json.loads(json_text)
                
                if json_data and isinstance(json_data, dict) and json_data.get('status') == 1 and json_data.get('data'):
                    tip = json_data['data']['user_tip']
                    self.logger.debug(f"Sleeping for {self.ai_sleep}s after generating tips")
                    time.sleep(self.ai_sleep)
                    return [tip] if tip else []
                return []
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON response: {str(e)}")
                return []
            
        except Exception as e:
            self.logger.error(f"Error generating user tips: {str(e)}")
            return []

    def create_precautions(self, medicine_data: Dict) -> List[str]:
        """Generate precautions based on medicine details"""
        try:
            prompt = f"""
            You are an expert in providing user-friendly and actionable insights based on detailed information. Your task is to extract one important precaution from the given medicine information and present it clearly and concisely.

            Medicine Information:
            - Product Name: {medicine_data['product_name']}
            - Generic Name: {medicine_data['generic_name']}
            - Description: {medicine_data['description']}
            - Details: {medicine_data['details']}

            Your response must:
            1. Be concise and under 30 words.
            2. Focus on actionable and practical precautions based on the provided medicine information.
            3. Avoid repeating the provided details verbatim unless essential for clarity.
            4. Be formatted strictly as JSON. Do not include any additional text, explanations, or comments outside of the JSON structure.

            Output: Provide the precaution in the following JSON format:
            {{
            "status": 1,
            "message": "Successfully generated precaution",
            "data": {{
                "precaution": "Example precaution here"
            }}
            }}

            If the information provided is insufficient to generate a precaution, return:
            {{
            "status": 0,
            "message": "Insufficient information to generate a precaution",
            "data": null
            }}

            Strictly adhere to the JSON format and ensure no additional text or explanations are included outside of the JSON structure.
            """

            response = self.model.generate_content(prompt)
            try:
                # Extract JSON content from potential markdown code block
                json_text = extract_json_from_text(response.text)
                json_data = json.loads(json_text)
                
                if json_data and isinstance(json_data, dict) and json_data.get('status') == 1 and json_data.get('data'):
                    precaution = json_data['data']['precaution']
                    self.logger.debug(f"Sleeping for {self.ai_sleep}s after generating precautions")
                    time.sleep(self.ai_sleep)
                    return [precaution] if precaution else []
                return []
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON response: {str(e)}")
                return []
            
        except Exception as e:
            self.logger.error(f"Error generating precautions: {str(e)}")
            return []

    def extract_diseases(self, medicine_data: Dict) -> List[str]:
        """Extract diseases that the medicine is used for"""
        try:
            prompt = f"""
            You are an expert in extracting and formatting medical information. Your task is to identify and list diseases or conditions this medicine is used for, based on the provided information.

            Medicine Information:
            - Product Name: {medicine_data['product_name']}
            - Generic Name: {medicine_data['generic_name']}
            - Description: {medicine_data['description']}
            - Details: {medicine_data['details']}

            Your response must:
            1. Extract only the names of diseases or conditions this medicine is used for.
            2. List the diseases or conditions in an array within the JSON format.
            3. Avoid including additional details, explanations, or repeated text from the input.

            Output: Provide the list in the following JSON format:
            {{
            "status": 1,
            "message": "Successfully extracted list of diseases/conditions",
            "data": {{
                "diseases_conditions": ["Example Disease 1", "Example Disease 2"]
            }}
            }}

            If the information provided is insufficient to identify any diseases or conditions, return:
            {{
            "status": 0,
            "message": "No diseases/conditions found",
            "data": null
            }}

            Strictly adhere to the JSON format and ensure no additional text, explanations, or comments outside of the JSON structure.
            """
            
            response = self.model.generate_content(prompt)
            try:
                # Extract JSON content from potential markdown code block
                json_text = extract_json_from_text(response.text)
                json_data = json.loads(json_text)
                
                if json_data and isinstance(json_data, dict) and json_data.get('status') == 1 and json_data.get('data'):
                    diseases = json_data['data']['diseases_conditions']
                    self.logger.debug(f"Sleeping for {self.ai_sleep}s after extracting diseases")
                    time.sleep(self.ai_sleep)
                    return diseases if diseases else []
                return []
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON response: {str(e)}")
                return []
            
        except Exception as e:
            self.logger.error(f"Error extracting diseases: {str(e)}")
            return []

    def process_medicine(self, medicine_data: Dict) -> Dict:
        """Process a single medicine entry with all AI features"""
        try:
            processed_data = medicine_data.copy()
            processed_data.update({
                'user_tips': self.generate_user_tips(medicine_data),
                'precautions': self.create_precautions(medicine_data),
                'diseases': self.extract_diseases(medicine_data)
            })
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing medicine data: {str(e)}")
            return medicine_data

    def process_batch(self, medicine_list: List[Dict]) -> List[Dict]:
        """Process a batch of medicine data"""
        processed_data = []
        for medicine in medicine_list:
            processed_medicine = self.process_medicine(medicine)
            processed_data.append(processed_medicine)
        return processed_data
