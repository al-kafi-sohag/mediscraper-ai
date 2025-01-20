import pandas as pd

# Read the CSV file
df = pd.read_csv('data/med-2.csv')

# Extract unique dosage names from the 'Dosage Description' column
unique_doses = df['Dosage Description'].unique()

# Prepare data for the new CSV
doses_data = {
    'name': unique_doses,
    'slug': [dose.lower().replace(" ", "-") for dose in unique_doses],
    'status': [1] * len(unique_doses)
}

# Create a new DataFrame
doses_df = pd.DataFrame(doses_data)

# Save to a new CSV file
doses_df.to_csv('data/doses.csv', index=False)