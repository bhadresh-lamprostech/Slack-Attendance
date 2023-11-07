import pandas as pd
from datetime import datetime,timedelta

# Load the Excel file and specify the sheet name
file_path = "attendance.xlsx"

xls = pd.ExcelFile(file_path)
# Get a list of sheet names in the Excel file
sheet_names = xls.sheet_names

# Get today's date
today = datetime.today().date()

# Initialize a dictionary to store working hours for each sheet and date
data = {
    'Name': [],
}


def remove_data(df,sheet_name):
    df = pd.read_excel(file_path)

    # Convert the 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Calculate the date 7 days ago from the current date
    seven_days_ago = datetime.now() - timedelta(days=5)

    # Filter the DataFrame to remove entries older than 7 days
    df = df[df['Date'] >= seven_days_ago]

    # Format the 'Date' column to '%Y-%m-%d' format
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    # Save the updated DataFrame back to the same Excel file, overwriting the original data
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)



# Iterate through each sheet and preprocess the data
for sheet_name in sheet_names:
    if sheet_name == "Attendance":
        continue  # Skip the "Attendance" sheet

    

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    remove_data(df, sheet_name)

    working_hours_per_date = {}

    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

    date = datetime.now().strftime('%Y-%m-%d')

    date_filtered_df = df[df['Date'] == date]

    print(date_filtered_df.empty)
    if date_filtered_df.empty:
        working_hours_per_date[date] = 0
    else:
        check_in_time = None
        check_out_time = None
        break_start_time = None
        break_end_time = None
        working_hours = 0
        
        for index, row in date_filtered_df.iterrows():
            if row['Action'] == "Check-In":
                check_in_time = row['Datetime']
            elif row['Action'] == "Check-Out":
                check_out_time = row['Datetime']
            elif row['Action'] == "Break Start":
                break_start_time = row['Datetime']
            elif row['Action'] == "Break End":
                break_end_time = row['Datetime']
                working_hours += (break_end_time - break_start_time).total_seconds()

        working_hours = (check_out_time - check_in_time).total_seconds() - working_hours
        working_hours = working_hours / 3600
        working_hours_per_date[date] = working_hours

    data['Name'].append(sheet_name)
    if date not in data:
        data[date] = []
    data[date].append(working_hours_per_date.get(date, 0))


print(data)
# Create the DataFrame
df = pd.DataFrame(data)

# Check if today's date already exists in the "Attendance" sheet
if today in df.columns:
    # Update the data for today without overwriting
    existing_data = pd.read_excel(file_path, sheet_name="Attendance")
    existing_data[today] = df[today]
    df = existing_data

# Append the DataFrame as a new sheet named "Attendance"
with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name="Attendance", index=False)

print(f"Data for {today} has been appended to the 'Attendance' sheet.")
