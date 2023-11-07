import pandas as pd

def print_attendance(input_file, target_date, sheets):
    # Load the sheets into a dictionary of DataFrames
    sheet_data = {}
    for sheet_name in sheets:
        sheet_data[sheet_name] = pd.read_excel(input_file, sheet_name=sheet_name)

    # Create an empty attendance dictionary to store the results
    attendance_data = {}

    # Check attendance for each person and store the results
    for sheet_name in sheets:
        if target_date in sheet_data[sheet_name]['Date'].values:
            attendance = sheet_data[sheet_name].loc[sheet_data[sheet_name]['Date'] == target_date, 'Time'].sum()
        else:
            attendance = 0
        attendance_data[sheet_name] = attendance

    # Print the attendance data
    for name, attendance in attendance_data.items():
        print(f"{name}'s attendance on {target_date}: {attendance} hours")

# Example usage
input_file = 'attendance.xlsx'
target_date = '2023-11-07'
sheets = ['Bhadresh', 'Deepak']

print_attendance(input_file, target_date, sheets)
