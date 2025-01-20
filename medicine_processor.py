import pandas as pd
from datetime import datetime

class MedicineProcessor:
    def __init__(self, med_file, company_file, generic_file, strength_file, dose_file, output_file):
        self.med_file = med_file
        self.company_file = company_file
        self.generic_file = generic_file
        self.strength_file = strength_file
        self.dose_file = dose_file
        self.output_file = output_file
        self.med_data = None
        self.company_names = None
        self.generic_names = None
        self.medicine_strengths = None
        self.doses = None

    def load_data(self):
        """Load all data files into memory."""
        self.med_data = pd.read_csv(self.med_file)
        self.company_names = pd.read_csv(self.company_file)
        self.generic_names = pd.read_csv(self.generic_file)
        self.medicine_strengths = pd.read_csv(self.strength_file)
        self.doses = pd.read_csv(self.dose_file)

    def replace_ids(self):
        """Replace columns with their corresponding IDs."""
        # Ensure unique indexes in lookup DataFrames
        company_lookup = self.company_names.drop_duplicates(subset='name').set_index('name')['id']
        generic_lookup = self.generic_names.drop_duplicates(subset='name').set_index('name')['id']
        strength_lookup = self.medicine_strengths.drop_duplicates(subset='name').set_index('name')['id']
        dose_lookup = self.doses.drop_duplicates(subset='name').set_index('name')['id']

        # Replace manufacturer names with IDs
        self.med_data['company_id'] = self.med_data['Name of the Manufacturer'].map(company_lookup)

        # Replace generic names with IDs
        self.med_data['generic_id'] = self.med_data['Generic Name'].map(generic_lookup)

        # Replace strengths with IDs
        self.med_data['strength_id'] = self.med_data['Strength'].map(strength_lookup)

        # Replace doses with IDs
        self.med_data['dose_id'] = self.med_data['Dosage Description'].map(dose_lookup)


    def transform_data(self):
        """Transform data into the required output format."""
        # Add a 'slug' based on the 'name' (Brand Name)
        self.med_data['slug'] = self.med_data['Brand Name'].str.replace(' ', '-').str.lower()

        # Try to clean the Price column: remove 'Tk' and other non-numeric characters
        self.med_data['price_cleaned'] = (
            self.med_data['Price']
            .str.replace(r'[^\d.]', '', regex=True)
        )

        # Split the rows into valid and invalid based on the ability to convert to float
        valid_rows = self.med_data[self.med_data['price_cleaned'].apply(lambda x: x.replace('.', '', 1).isdigit())]
        invalid_rows = self.med_data[~self.med_data['price_cleaned'].apply(lambda x: x.replace('.', '', 1).isdigit())]

        # Process valid rows
        valid_rows['price'] = valid_rows['price_cleaned'].astype(float)  # Convert to float
        valid_rows['status'] = valid_rows['price'].apply(lambda x: 1 if x > 0 else 0)  # Status based on price
        valid_rows['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add the current timestamp

        # Rename columns for the final output
        valid_rows = valid_rows.rename(columns={
            'Brand Name': 'name',
            'Use For': 'use_for',
            'DAR': 'dar'
        })

        # Select and reorder columns for output
        valid_rows = valid_rows[[
            'name', 'slug', 'generic_id', 'company_id', 'strength_id', 'dose_id',
            'price', 'status', 'created_at', 'use_for', 'dar'
        ]]

        # Save valid rows to one file and invalid rows to another
        valid_rows.to_csv('data/valid-medicines.csv', index=False)
        invalid_rows.to_csv('data/invalid-medicines.csv', index=False)

        print("Processing complete. Valid rows saved to 'data/valid-medicines.csv'. Invalid rows saved to 'data/invalid-medicines.csv'.")


    def save_data(self):
        """Save the processed data to the output file."""
        self.med_data.to_csv(self.output_file, index=False)

    def process(self):
        """Orchestrate the data processing workflow."""
        self.load_data()
        self.replace_ids()
        self.transform_data()
        self.save_data()

# Usage
if __name__ == "__main__":
    processor = MedicineProcessor(
        med_file='data/med-2.csv',
        company_file='server/company_names.csv',
        generic_file='server/generic_names.csv',
        strength_file='server/medicine_strengths.csv',
        dose_file='server/medicine_doses.csv',
        output_file='data/complete-medicines.csv'
    )
    processor.process()
