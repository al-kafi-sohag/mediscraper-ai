import pandas as pd
import os

class GenericNameProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def read_data(self):
        """Read the data from the CSV file."""
        try:
            data = pd.read_csv(self.input_file, sep=',')  # Adjust the delimiter if necessary
            return data
        except Exception as e:
            print(f"Error reading the data: {e}")
            return None

    def get_unique_generic_names(self, data):
        """Extract unique generic names from the data."""
        if data is not None:
            unique_generic_names = data.iloc[:, 3].unique()  # Accessing the fourth column (index 3)
            return unique_generic_names
        return []

    def create_slug(self, name):
        """Create a slug from the generic name."""
        return name.lower().replace(' ', '-')

    def write_unique_generic_names(self, generic_names):
        """Write the unique generic names to a new CSV file."""
        try:
            df = pd.DataFrame({
                'name': generic_names,
                'slug': [self.create_slug(name) for name in generic_names],
                'status': [1] * len(generic_names)  # Default status value
            })
            df.to_csv(self.output_file, index=False)
            print(f"Unique generic names have been written to {self.output_file}")
        except Exception as e:
            print(f"Error writing the data: {e}")

if __name__ == "__main__":
    input_file = "data/med-2.csv"  # Path to your input CSV file
    output_file = "data/generic_names.csv"  # Path to your output CSV file

    processor = GenericNameProcessor(input_file, output_file)
    data = processor.read_data()
    unique_generic_names = processor.get_unique_generic_names(data)
    processor.write_unique_generic_names(unique_generic_names)