# excel_cleaner.py 

Automates data cleaning for CSV and Excel files by validating and standardizing key fields such as phone numbers, PAN cards, emails, pincodes, and salaries. Saves cleaned data as a CSV file.

Required Python libraries:
Libraries: pandas, numpy, re

Installation:
Install dependencies:
    pip install pandas numpy
Set input_file and output_file paths in the script.

Usage:
Place .csv or .xlsx files in the designated folder.
Run:
    python excel_cleaner.py
Cleaned data is saved to the output file.


# testing.py
Excel & CSV Data Cleaning Script
This is the updated version.
This project is designed to automate the process of cleaning and standardizing data from multiple Excel and CSV files. The script reads data from a specified directory, performs validation and transformation on key fields such as phone numbers, PAN cards, email addresses, pincodes, and salaries, and saves the cleaned dataset as a CSV file.

Required Python libraries:
pandas
numpy
os
re

Installation:
Clone the repository or download the script.
Install the required libraries using pip:
   pip install pandas numpy
Set the input_directory variable to the folder containing your input files.
Set the output_file variable to specify the name of the cleaned CSV file.

Usage:
Place all .csv and .xlsx files in the specified input_directory.
Run the script:
    python testing.py
The cleaned and standardized data will be saved to the specified output file.



Output:
Final cleaned dataset includes:
name, company, phone, pincode, income, gender, pan, employment, dob, email, details_completion, state, source
