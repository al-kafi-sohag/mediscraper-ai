import pandas as pd

class MedicineStrengthProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.strengths_data = []

    def load_data(self):
        """Load data from the input CSV file."""
        data = pd.read_csv(self.input_file)
        self.strengths_data = data.iloc[:, 4].unique()

    def process_strengths(self):
        """Process the unique strength names into quantity and unit."""
        processed_strengths = []

        for strength in self.strengths_data:
            parts = strength.split()
            quantity = parts[0] if parts else ''
            unit = ' '.join(parts[1:]) if len(parts) > 1 else ''
            processed_strengths.append({
                'quantity': quantity,
                'unit': unit,
                'name': quantity + ' ' + unit,
                'status': 1
            })

        return processed_strengths

    def save_to_csv(self):
        """Save the processed strengths to a new CSV file."""
        strengths_df = pd.DataFrame(self.process_strengths())
        strengths_df.to_csv(self.output_file, index=False)

    def run(self):
        """Execute the processing workflow."""
        self.load_data()
        self.save_to_csv()

if __name__ == "__main__":
    input_file = 'data/med-2.csv'
    output_file = 'data/medicine_strengths.csv'
    processor = MedicineStrengthProcessor(input_file, output_file)
    processor.run()