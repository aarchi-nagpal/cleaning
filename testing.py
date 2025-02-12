import pandas as pd
import re
import numpy as np
import os

# Define the directory containing input files
input_directory = '---'   #mention your directory path

# Get a list of all Excel and CSV files in the directory
input_files = [
    os.path.join(input_directory, f)
    for f in os.listdir(input_directory)
    if os.path.isfile(os.path.join(input_directory, f)) and f.endswith(('.xlsx', '.csv'))
]

# Create an empty list to store data from each file.
combined_data = []


# Loop through each file and read first 100000 rows.
for file in input_files:
    try:  # Handle potential errors reading individual files
        if file.endswith('.xlsx'):
            df = pd.read_excel(file, nrows=100000)
        elif file.endswith('.csv'):
            df = pd.read_csv(file, nrows=100000, encoding='ISO-8859-1', low_memory=False) 

        if 'Company' in df.columns: 
            df['Company'] = df['Company'].astype(str).apply(lambda company: re.sub(r'[\\/*?:"<>|]', "NULL", company))
            df['Company'] = df['Company'].replace("", "NULL")
            df['Company'] = df['Company'].fillna("NULL")
            
        df['source'] = os.path.basename(file) 
        combined_data.append(df)
    except Exception as e:
        print(f"Error reading file {file}: {e}")

# Combine all data into one DataFrame.
final_combined_df = pd.concat(combined_data, ignore_index=True)



# Initialize counters for invalid entries
invalid_phone_count = 0
invalid_pancard_count = 0
invalid_email_count = 0
invalid_pincode_count=0

# Function to validate phone numbers
def validate_phone(phone):
    global invalid_phone_count
    if pd.isna(phone):  
        invalid_phone_count += 1
        return "NULL"
    
    if isinstance(phone, (int, float)) or (isinstance(phone, str) and phone.isdigit()):
        phone = str(int(float(phone))) 
        if len(phone) == 10:
            return int(phone) 
    invalid_phone_count += 1
    return "NULL"  
  

def validate_pancard(pancard):
    global invalid_pancard_count
    if pd.isna(pancard):  
        invalid_pancard_count += 1
        return "NULL"

    if isinstance(pancard, str) and len(pancard) == 10:
        pattern = r'^[A-Za-z]{5}\d{4}[A-Za-z]{1}$'
        
        # If the pancard matches the pattern, it's valid
        if re.match(pattern, pancard):
            return pancard  
    invalid_pancard_count += 1
    return "NULL"

def validate_pincode(pincode):
    global invalid_pincode_count
    if pd.isna(pincode): 
        invalid_pincode_count += 1
        return "NULL"
    if isinstance(pincode, (int, float)) or (isinstance(pincode, str) and pincode.isdigit()):
        pincode = str(int(float(pincode)))  
        if len(pincode) == 6:  
            return pincode  
    invalid_pincode_count += 1
    return "NULL"

def validate_company(company):
    if pd.isna(company) or not isinstance(company, str) or company.strip() == "":
        return "NULL"

    # Remove unwanted non-alphanumeric characters except spaces, &, ., -, _, and /
    cleaned_company = re.sub(r'[^a-zA-Z0-9\s&._/-]', '', company).strip()

    # Replace empty strings after cleaning with "NULL"
    return cleaned_company if cleaned_company else "NULL"
    
def check_completion_status(row):
    return "NULL" if "NULL" in row.values else "OK"


# Function to process and save the file
def process_and_save_file(df, output_file):
    try:
        data = df.copy() 
        # Drop rows that are completely blank
        data.dropna(how='all', inplace=True) 
     
        # Convert 'Pincode' column to string, handle blank/null values, and replace blanks with 'NULL'
        if 'Pincode' in data.columns:
            data['pincode'] = data['Pincode'].apply(validate_pincode)

        # Validate the "Phone" column for valid 10-digit integers if it exists
        if 'phone' in data.columns:
            data['phone'] = data['phone'].apply(validate_phone)

        # Handle the 'salary' column
        if 'salary' in data.columns:
        # Replace blank values (empty strings or whitespace-only strings) with NaN
            data['salary'] = data['salary'].replace(r'^\s*$', np.nan, regex=True)

        # Convert to numeric (forces non-numeric values like text to NaN)
            data['salary'] = pd.to_numeric(data['salary'], errors='coerce')

        # Fill NaN values and values <= 25000 with 25000
            data['income'] = data['salary'].apply(lambda x: 25000 if pd.isna(x) or x <= 25000 else round(x, 0))


        # Replace 1 with 'Male' and 0 with 'Female' in 'u_gender' column
        if 'u_gender' in data.columns:
            data['gender'] = data['u_gender'].fillna('NULL')
            
        # Process the 'Pancard' column
        if 'Pancard' in data.columns:
            data['Pancard'] = data['Pancard'].astype(str).str.strip().str.upper()
            # Validate the 'Pancard' column using the validate_pancard function
            data['pan'] = data['Pancard'].apply(validate_pancard)

        
        # process the 'u_emp_tpe' column
        if 'u_emp_tpe' in data.columns:
            data['employment'] = 'salaried'


       # Extract and standardize date of 'DOB' column
        if 'DOB' in data.columns:
            # Preprocess DOB to replace '/' with '-' so that pandas can handle both formats
            data['DOB'] = data['DOB'].astype(str).str.replace('/', '-', regex=False)

            data['DOB'] = pd.to_datetime(data['DOB'], errors='coerce',dayfirst=True)

        # Format the valid dates as 'YYYY-MM-DD'
            data['dob'] = data['DOB'].dt.strftime('%Y-%m-%d')

        # Replace invalid dates (NaT) with 'NULL'
            data['dob'] = data['dob'].fillna('NULL')

 
        # Process the 'u_email_id' column
        if 'u_email_id' in data.columns:
            def clean_email(email):
                if pd.isna(email):  # If email is NaN, return NULL
                    return "NULL"
                if isinstance(email, str):
                    email = email.strip()  # Remove leading/trailing spaces
                    if email.count("@") > 1:  # Check for more than one @ sign
                        # Keep only the first @ and remove the rest
                        email_parts = email.split("@", 1)
                        email = email_parts[0] + "@" + email_parts[1].replace("@", "")
                    return email
                return "INVALID"  # Handle non-string values

            # Clean the email IDs
            data['u_email_id'] = data['u_email_id'].apply(clean_email)

            # Extract the host (before @) and domain (after @)
            data['host'] = data['u_email_id'].apply(
                lambda email: email.split("@")[0] if "@" in email else email
            )
            data['domain'] = data['u_email_id'].apply(
                lambda email: email.split("@")[1] if "@" in email else email
            )

            # Shift digits from domain to host
            def shift_digits_to_host(row):
                domain = row['domain']
                host = row['host']
                # Extract digits from domain
                digits = ''.join(re.findall(r'\d+', domain))
                if digits:
                    # Remove digits from domain and add them to host
                    row['domain'] = re.sub(r'\d+', '', domain)
                    row['host'] = host + digits
                return row

            # Apply the function to each row
            data = data.apply(shift_digits_to_host, axis=1)

            # Convert the 'domain' column to lowercase
            data['domain'] = data['domain'].str.lower()

            # Create a new column 'com' to store the data after the last dot
            data['com'] = data['domain'].apply(lambda x: x.rsplit('.', 1)[-1] if '.' in x else x)

            # Strip the domain column at the last dot
            data['domain'] = data['domain'].apply(lambda x: x.rsplit('.', 1)[0] if '.' in x else x)

            # Replace domains based on specified conditions
            def replace_domains(row):
                domain = row['domain']
                com_value = row.get('com', None)

                if pd.isna(domain):  # Check for NaN values
                    return "NULL"

                if not isinstance(domain, str): 
                    invalid_email_count += 1
                    return "NULL"

                # Additional logic to concatenate domain and 'com' column
                if com_value in ['org', 'net', 'in', 'ai', 'biz']: 
                    return f"{domain}.{com_value}"

                # Handle domain corrections
                if any(var in domain for var in ['yahoo', 'yhoo', 'yahooo']):
                    return 'yahoo.com'

                if any(var in domain for var in ['rediffmail', 'redifmail']):
                    return 'rediffmail.com'

                if 'hotmail' in domain:
                    return 'hotmail.com'

                if len(set('gmail') & set(domain.lower())) >= 4 and len(domain) <= 6:
                    return 'gmail.com'

                return domain + ".com"

            # Apply the domain replacement logic
            data['corr_domain'] = data.apply(replace_domains, axis=1)

            # Concatenate 'host' and 'corr_domain' into a new column 'email_id'
            data['email'] = data['host'] + '@' + data['corr_domain']

            # Ensure email is NULL if domain is NULL
            data.loc[data['domain'] == 'NULL', 'email'] = 'NULL'

        # Extract customer_name, state, and company from the relevant columns
        data.rename(columns={"U_display_name": "name"}, inplace=True)
        if 'name' in data.columns:
            data['name'] = data['name'].astype(str).apply(lambda x: str(x).strip() if isinstance(x, (str, int, float)) else "NULL")
        if 'state' in data.columns:
            data['state'] = data['state'].apply(lambda x: str(x).strip() if isinstance(x, (str, int, float)) else "NULL")
                    
        if 'Company' in data.columns:  
            data['Company'] = data['Company'].astype(str).apply(validate_company)
            data.rename(columns={"Company": "company"}, inplace=True)

        data['details_completion'] = data.apply(check_completion_status, axis=1)
            
        # Print the counts of invalid entries
        print(f"Invalid phone numbers: {invalid_phone_count}")
        print(f"Invalid Pancards: {invalid_pancard_count}")
        print(f"Invalid emails: {invalid_email_count}")
        print(f"Invalid pincodes: {invalid_pincode_count}")



        # Define the columns to keep
        columns_to_keep = [
            "name", "company", "phone", "pincode", "income", "gender", "pan", "employment",
            "dob", "email", "details_completion", "source","state"
        ]

        # Keep only the specified columns if they exist
        data = data[[col for col in columns_to_keep if col in data.columns]]

        # Save the cleaned data to the output file
        data.to_csv(output_file, index=False,encoding='utf-8')
        print(f"Cleaned data saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Execute the cleaning process using the combined file
output_file = '---.csv'  # mention output file name.
process_and_save_file(final_combined_df, output_file)
