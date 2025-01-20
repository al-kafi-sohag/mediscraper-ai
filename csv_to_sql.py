import pandas as pd
import os
from datetime import datetime

class CSVToSQL:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.table_name = os.path.splitext(os.path.basename(csv_file_path))[0]  # Get table name from CSV file name
        self.data = pd.read_csv(csv_file_path)

    def generate_sql(self):
        """Generate SQL commands to insert data."""
        sql_commands = []

        # Insert data commands
        for index, row in self.data.iterrows():
            # Handle nan values
            values = []
            for value in row.values:
                if pd.isna(value):
                    values.append('" "')
                elif isinstance(value, str):
                    values.append(f'"{value}"')
                else:
                    values.append(str(value))

            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp
            insert_cmd = f"INSERT INTO {self.table_name} ({', '.join(self.data.columns)}, created_at) VALUES ({', '.join(values)}, '{created_at}');"
            sql_commands.append(insert_cmd)

        return sql_commands

    def save_to_sql_file(self):
        """Save the generated SQL commands to a .sql file."""
        sql_commands = self.generate_sql()
        sql_file_path = f"sql/{self.table_name}.sql"
        
        with open(sql_file_path, 'w') as sql_file:
            for command in sql_commands:
                sql_file.write(command + "\n")
        
        print(f"SQL commands have been saved to {sql_file_path}")

if __name__ == "__main__":
    csv_file_path = "data/medicine_doses.csv"  # Path to your CSV file

    csv_to_sql = CSVToSQL(csv_file_path)
    csv_to_sql.save_to_sql_file()