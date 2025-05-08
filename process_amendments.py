import pandas as pd
import json
from datetime import datetime

# Read the Excel file from the 'Award Details' sheet
df = pd.read_excel('Award_Details_20250505.xlsx', sheet_name='Award Details')

# Convert date column to datetime
df['Day of Award Issue Date'] = pd.to_datetime(df['Day of Award Issue Date'], errors='coerce')

# Create a dictionary of amendments by FAIN
amendments = {}
for _, row in df.iterrows():
    fain = row['FAIN']
    issue_date = row['Day of Award Issue Date']
    
    # Only process rows with valid FAIN and date
    if pd.notna(fain) and pd.notna(issue_date):
        if fain not in amendments:
            amendments[fain] = []
        amendments[fain].append({
            'date': issue_date.strftime('%Y-%m-%d'),
            'type': row['Amendment Type'] if pd.notna(row['Amendment Type']) else 'Unknown'
        })

# Save to JSON
with open('amendment_data.json', 'w') as f:
    json.dump(amendments, f, indent=2)

print(f"Amendment data has been processed and saved to amendment_data.json")
print(f"Number of FAINs with amendments: {len(amendments)}")
print("Sample of the data:")
sample_fains = list(amendments.keys())[:3]
for fain in sample_fains:
    print(f"\nFAIN: {fain}")
    print(f"Number of amendments: {len(amendments[fain])}")
    print("First amendment:", amendments[fain][0]) 