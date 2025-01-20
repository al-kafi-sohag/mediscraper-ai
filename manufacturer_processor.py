import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class ManufacturerProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        
    def create_slug(self, name):
        """Create a slug from the manufacturer name."""
        return name.lower().replace(' ', '-')

    def read_data(self):
        """Read the data from the CSV file."""
        try:
            data = pd.read_csv(self.input_file, sep=',') 
            print(data.head())  # Print the first few rows of the DataFrame
            return data
        except Exception as e:
            print(f"Error reading the data: {e}")
            return None

    def get_unique_manufacturers(self, data):
        """Extract unique manufacturer names from the data using column index."""
        if data is not None:
            unique_manufacturers = data.iloc[:, 1].unique()  # Accessing the second column
            return unique_manufacturers
        return []
    
    def write_unique_manufacturers(self, manufacturers):
        """Write the unique manufacturer names to a new CSV file with additional columns for database import."""
        try:
            # Create a DataFrame with additional columns
            slugs = [self.create_slug(name) for name in manufacturers]  # Create slugs
            status = [1] * len(manufacturers)  # Default status value

            # Check lengths before creating DataFrame
            if len(manufacturers) == len(slugs) == len(status):
                df = pd.DataFrame({
                    'name': manufacturers,
                    'slug': slugs,
                    'status': status
                })
                df.to_csv(self.output_file, index=False)
                print(f"Unique manufacturers have been written to {self.output_file}")
            else:
                print("Error: Length mismatch between manufacturers, slugs, and status lists.")
        except Exception as e:
            print(f"Error writing the data: {e}")

if __name__ == "__main__":
    input_file = 'data/med-2.csv'
    output_file = 'data/company_names.csv'
    
    processor = ManufacturerProcessor(input_file, output_file)
    data = processor.read_data()
    unique_manufacturers = processor.get_unique_manufacturers(data)
    processor.write_unique_manufacturers(unique_manufacturers)